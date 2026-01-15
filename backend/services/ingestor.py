from sqlalchemy.orm import Session
from ..models import Source, RawItem
import feedparser
import hashlib
import json
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class IngestorService:
    def __init__(self, db: Session):
        self.db = db

    def register_source(self, name: str, source_type: str, url: str) -> Source:
        """Register a new source if not exists."""
        source = self.db.query(Source).filter(Source.url == url).first()
        if not source:
            source = Source(name=name, source_type=source_type, url=url)
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)
        return source

    def ingest_feed(self, source_id: int):
        """Fetch and process RSS feed for a source."""
        source = self.db.query(Source).filter(Source.source_id == source_id).first()
        if not source or not source.url:
            return 0

        feed = feedparser.parse(source.url)
        new_count = 0

        for entry in feed.entries:
            # Hash calculation for dedup
            content_str = f"{entry.title}{entry.get('description', '')}{entry.get('link', '')}"
            content_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

            # Check duplication
            exists = self.db.query(RawItem).filter(RawItem.content_hash == content_hash).first()
            if exists:
                continue

            # Naive canonical URL handling (prefer link in entry)
            # In a real heavy scrape, we might follow redirects here
            canonical = entry.get('link', '')

            # Parse time
            pub_struct = entry.get('published_parsed') or entry.get('updated_parsed')
            published_at = datetime.fromtimestamp(
                datetime(*pub_struct[:6]).timestamp(), tz=timezone.utc
            ) if pub_struct else datetime.now(timezone.utc)

            raw_item = RawItem(
                source_id=source.id,
                content_hash=content_hash,
                title=entry.title,
                content=entry.get('description', '') or entry.get('summary', ''),
                url=entry.get('link', ''),
                canonical_url=canonical,
                published_at=published_at
            )
            self.db.add(raw_item)
            new_count += 1
        
        self.db.commit()
        return new_count

    def ingest_all(self):
        """Run ingest for all registered sources."""
        sources = self.db.query(Source).all()
        total_new = 0
        for s in sources:
            try:
                total_new += self.ingest_feed(s.source_id)
            except Exception as e:
                logger.error(f"Failed to ingest source {s.name}: {e}")
        return total_new
