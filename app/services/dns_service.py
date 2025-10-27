import asyncio
import socket
from typing import Dict, List, Optional
from urllib.parse import urlparse
from app.core.logging import get_logger

try:
    import dns.resolver
    import dns.asyncresolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

logger = get_logger(__name__)


class DNSService:
    """Service for DNS lookups and email security checks"""
    
    async def check_dns_records(self, url: str) -> Dict:
        """Check DNS records for SEO and security"""
        if not DNS_AVAILABLE:
            logger.warning("DNS resolver not available, returning empty results")
            return {}
            
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            results = {}
            
            # Check SPF record
            spf_record = await self._check_spf_record(domain)
            results['spf_record'] = spf_record is not None
            results['spf_content'] = spf_record
            
            # Check DMARC record
            dmarc_record = await self._check_dmarc_record(domain)
            results['dmarc_record'] = dmarc_record is not None
            results['dmarc_content'] = dmarc_record
            
            # Check MX records
            mx_records = await self._check_mx_records(domain)
            results['mx_records'] = len(mx_records) > 0
            results['mx_count'] = len(mx_records)
            
            # Check A record
            a_records = await self._check_a_records(domain)
            results['a_records'] = len(a_records) > 0
            results['a_count'] = len(a_records)
            
            # Check AAAA record (IPv6)
            aaaa_records = await self._check_aaaa_records(domain)
            results['aaaa_records'] = len(aaaa_records) > 0
            results['ipv6_support'] = len(aaaa_records) > 0
            
            # Check CNAME record
            cname_record = await self._check_cname_record(domain)
            results['cname_record'] = cname_record is not None
            
            # Check TXT records for verification
            txt_records = await self._check_txt_records(domain)
            results['txt_records_count'] = len(txt_records)
            results['has_verification'] = any(
                'google-site-verification' in record.lower() or 
                'facebook-domain-verification' in record.lower() or
                'v=spf1' in record.lower()
                for record in txt_records
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error checking DNS records for {domain}: {e}")
            return {}
    
    async def _check_spf_record(self, domain: str) -> Optional[str]:
        """Check for SPF record"""
        try:
            resolver = dns.asyncresolver.Resolver()
            answers = await resolver.resolve(domain, 'TXT')
            
            for rdata in answers:
                txt_record = str(rdata).strip('"')
                if txt_record.startswith('v=spf1'):
                    return txt_record
            return None
        except:
            return None
    
    async def _check_dmarc_record(self, domain: str) -> Optional[str]:
        """Check for DMARC record"""
        try:
            resolver = dns.asyncresolver.Resolver()
            dmarc_domain = f"_dmarc.{domain}"
            answers = await resolver.resolve(dmarc_domain, 'TXT')
            
            for rdata in answers:
                txt_record = str(rdata).strip('"')
                if txt_record.startswith('v=DMARC1'):
                    return txt_record
            return None
        except:
            return None
    
    async def _check_mx_records(self, domain: str) -> List[str]:
        """Check MX records"""
        try:
            resolver = dns.asyncresolver.Resolver()
            answers = await resolver.resolve(domain, 'MX')
            return [str(rdata.exchange) for rdata in answers]
        except:
            return []
    
    async def _check_a_records(self, domain: str) -> List[str]:
        """Check A records"""
        try:
            resolver = dns.asyncresolver.Resolver()
            answers = await resolver.resolve(domain, 'A')
            return [str(rdata) for rdata in answers]
        except:
            return []
    
    async def _check_aaaa_records(self, domain: str) -> List[str]:
        """Check AAAA records (IPv6)"""
        try:
            resolver = dns.asyncresolver.Resolver()
            answers = await resolver.resolve(domain, 'AAAA')
            return [str(rdata) for rdata in answers]
        except:
            return []
    
    async def _check_cname_record(self, domain: str) -> Optional[str]:
        """Check CNAME record"""
        try:
            resolver = dns.asyncresolver.Resolver()
            answers = await resolver.resolve(domain, 'CNAME')
            return str(answers[0]) if answers else None
        except:
            return None
    
    async def _check_txt_records(self, domain: str) -> List[str]:
        """Check all TXT records"""
        try:
            resolver = dns.asyncresolver.Resolver()
            answers = await resolver.resolve(domain, 'TXT')
            return [str(rdata).strip('"') for rdata in answers]
        except:
            return []