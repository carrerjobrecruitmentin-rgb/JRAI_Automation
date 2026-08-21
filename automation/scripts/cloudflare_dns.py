import os
import sys
import argparse
import requests
from dotenv import load_dotenv

BASE_URL = "https://api.cloudflare.com/client/v4"

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def get_zone_id(token, zone_name):
    url = f"{BASE_URL}/zones"
    params = {"name": zone_name}
    response = requests.get(url, headers=get_headers(token), params=params)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise Exception(f"API Error: {data.get('errors')}")
    result = data.get("result", [])
    if not result:
        raise Exception(f"Zone '{zone_name}' not found.")
    return result[0]["id"]

def list_dns_records(token, zone_id):
    url = f"{BASE_URL}/zones/{zone_id}/dns_records"
    response = requests.get(url, headers=get_headers(token))
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise Exception(f"API Error: {data.get('errors')}")
    records = data.get("result", [])
    print(f"Existing DNS Records for zone {zone_id}:")
    for r in records:
        print(f"- {r['type']} {r['name']} -> {r['content']} (Proxied: {r['proxied']})")
    return records

def create_cname(token, zone_id, subdomain, zone_name, tunnel_id):
    url = f"{BASE_URL}/zones/{zone_id}/dns_records"
    record_name = f"{subdomain}.{zone_name}"
    payload = {
        "type": "CNAME",
        "name": record_name,
        "content": f"{tunnel_id}.cfargotunnel.com",
        "proxied": True,
        "comment": "Managed by script"
    }
    response = requests.post(url, headers=get_headers(token), json=payload)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise Exception(f"API Error: {data.get('errors')}")
    print(f"✅ Successfully created CNAME: {record_name} -> {tunnel_id}.cfargotunnel.com")

def delete_dns_record(token, zone_id, subdomain, zone_name):
    record_name = f"{subdomain}.{zone_name}"
    url = f"{BASE_URL}/zones/{zone_id}/dns_records"
    
    # First get the record to find its ID
    response = requests.get(url, headers=get_headers(token), params={"name": record_name, "type": "CNAME"})
    response.raise_for_status()
    data = response.json()
    
    if not data.get("success") or not data.get("result"):
        print(f"Record {record_name} not found.")
        return
        
    record_id = data["result"][0]["id"]
    
    # Delete the record
    delete_url = f"{BASE_URL}/zones/{zone_id}/dns_records/{record_id}"
    del_response = requests.delete(delete_url, headers=get_headers(token))
    del_response.raise_for_status()
    del_data = del_response.json()
    
    if not del_data.get("success"):
        raise Exception(f"API Error: {del_data.get('errors')}")
    print(f"✅ Successfully deleted DNS record: {record_name}")

def main():
    parser = argparse.ArgumentParser(description="Manage Cloudflare DNS records for tunnels.")
    parser.add_argument("--list", action="store_true", help="List existing DNS records")
    parser.add_argument("--delete", action="store_true", help="Delete a DNS record for the configured subdomain")
    args = parser.parse_args()

    load_dotenv()
    
    token = os.getenv("CF_API_TOKEN")
    zone_name = os.getenv("CF_ZONE", "jobrecruitment.ai")
    subdomain = os.getenv("CF_SUBDOMAIN", "admin")
    tunnel_id = os.getenv("CF_TUNNEL_ID")

    if not token:
        print("Error: CF_API_TOKEN environment variable is missing.")
        sys.exit(1)
        
    if not args.list and not args.delete and not tunnel_id:
        print("Error: CF_TUNNEL_ID environment variable is missing.")
        sys.exit(1)

    try:
        zone_id = get_zone_id(token, zone_name)
        
        if args.list:
            list_dns_records(token, zone_id)
        elif args.delete:
            delete_dns_record(token, zone_id, subdomain, zone_name)
        else:
            create_cname(token, zone_id, subdomain, zone_name, tunnel_id)
            
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        if e.response is not None:
            print(f"Response data: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
