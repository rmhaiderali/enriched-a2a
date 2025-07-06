import httpx
import ipaddress
import validators


async def get_ips_by_domain(domain: str) -> dict:
    """Get IP addresses associated with a domain (must be a valid FQDN)."""
    if not validators.domain(domain):
        raise ValueError(
            f"Invalid domain name: {domain}. Must be a valid hostname (FQDN)."
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://ipleak.net/json/{domain}")
        response.raise_for_status()
        data = response.json()
        error = data.get("error")
        ips = data.get("ips")

        if error:
            return {"error": error}
        else:
            return {"ips": list(ips.keys())}


async def get_location_by_ip(ip: str) -> dict:
    """Get location information from an IP address string."""
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise ValueError(f"Invalid IP address: {ip}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://ipleak.net/json/{ip}")
        response.raise_for_status()
        return response.json()


tools = [get_ips_by_domain, get_location_by_ip]
