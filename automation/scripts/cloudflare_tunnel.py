import argparse
import os
import subprocess
import sys
import yaml
import re
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = r"C:\Users\Dell\cloudflare-setup\.env"
CONFIG_PATH = r"C:\Users\Dell\.cloudflared\config.yml"

load_dotenv(ENV_PATH)

CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_ZONE = os.getenv("CF_ZONE", "jobrecruitment.ai")
CF_TUNNEL_NAME = os.getenv("CF_TUNNEL_NAME", "jobrecruitment-admin")

def create_tunnel(tunnel_name: str):
    print(f"🚀 Creating tunnel: {tunnel_name}")
    try:
        # Note: cloudflared outputs to stderr for some commands, so we capture both
        result = subprocess.run(
            ["cloudflared", "tunnel", "create", tunnel_name],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout + result.stderr
        
        # Extract tunnel ID. Typically output looks like: 
        # Created tunnel jobrecruitment-admin with id ef0324ec-03f7-4451-af4f-a18405783593
        match = re.search(r"id\s+([a-f0-9\-]{36})", output, re.IGNORECASE)
        if match:
            tunnel_id = match.group(1)
            print(f"✅ Tunnel created successfully. ID: {tunnel_id}")
            
            # Append to .env
            with open(ENV_PATH, "a") as f:
                f.write(f"\nCF_TUNNEL_ID={tunnel_id}\n")
            print(f"📝 Added CF_TUNNEL_ID to {ENV_PATH}")
            return tunnel_id
        else:
            print("⚠️ Could not extract tunnel ID from output:")
            print(output)
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating tunnel: {e}")
        print(e.stderr)
        return None

def add_ingress_route(tunnel_id: str, hostname: str, service_url: str):
    print(f"🌐 Adding ingress route for {hostname} -> {service_url}")
    try:
        if not os.path.exists(CONFIG_PATH):
            print(f"❌ Config file not found at {CONFIG_PATH}")
            return
            
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f) or {}

        if 'ingress' not in config:
            config['ingress'] = [
                {"service": "http_status:404"}
            ]
        
        # Ensure the last rule is the catch-all
        last_rule = config['ingress'][-1]
        if 'hostname' in last_rule:
             # If the last rule is not a catch-all, append one
             config['ingress'].append({"service": "http_status:404"})
             
        new_route = {
            "hostname": hostname,
            "service": service_url
        }
        
        # Insert before the last rule (catch-all)
        config['ingress'].insert(-1, new_route)
        
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f, sort_keys=False)
            
        print(f"✅ Route added to {CONFIG_PATH}")
    except Exception as e:
        print(f"❌ Error adding ingress route: {e}")

def run_tunnel():
    print("🏃 Running tunnel...")
    try:
        subprocess.run(["cloudflared", "tunnel", "run"])
    except KeyboardInterrupt:
        print("\n🛑 Tunnel stopped by user.")
    except Exception as e:
        print(f"❌ Error running tunnel: {e}")

def list_tunnels():
    print("📋 Listing tunnels...")
    try:
        subprocess.run(["cloudflared", "tunnel", "list"])
    except Exception as e:
        print(f"❌ Error listing tunnels: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage Cloudflare Tunnels")
    parser.add_argument("--create", action="store_true", help="Create a new tunnel")
    parser.add_argument("--add-route", action="store_true", help="Add an ingress route")
    parser.add_argument("--hostname", type=str, help="Hostname for ingress route (e.g., admin.jobrecruitment.ai)")
    parser.add_argument("--service", type=str, help="Service URL for ingress route (e.g., http://localhost:3000)")
    parser.add_argument("--run", action="store_true", help="Run the tunnel")
    parser.add_argument("--list", action="store_true", help="List tunnels")
    
    args = parser.parse_args()

    # Create the directory if it doesn't exist
    os.makedirs(r"C:\Users\Dell\cloudflare-setup", exist_ok=True)
    
    # Touch .env if it doesn't exist
    if not os.path.exists(ENV_PATH):
        with open(ENV_PATH, "w") as f:
            pass

    if args.create:
        create_tunnel(CF_TUNNEL_NAME)
    elif args.add_route:
        tunnel_id = os.getenv("CF_TUNNEL_ID")
        if not tunnel_id:
             print("⚠️ CF_TUNNEL_ID not found in .env. Cannot add route without a tunnel ID.")
             return
        if not args.hostname or not args.service:
            print("❌ --hostname and --service are required for --add-route")
            return
        add_ingress_route(tunnel_id, args.hostname, args.service)
    elif args.run:
        run_tunnel()
    elif args.list:
        list_tunnels()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
