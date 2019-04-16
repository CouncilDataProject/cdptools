#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, Optional, Union

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from .database import Database

###############################################################################

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)4s: %(module)s:%(lineno)4s %(asctime)s] %(message)s'
)
log = logging.getLogger(__file__)

###############################################################################


class CloudFirestoreDatabase(Database):

    def __init__(self, credentials_path: Union[str, Path], name: Optional[str] = None, **kwargs):
        # Resolve credentials
        credentials_path = Path(credentials_path).resolve(strict=True)

        # Initialize database reference
        cred = credentials.Certificate(str(credentials_path))

        # Check name
        # This is done as if the name is None we just want to initialize the main connection
        if name:
            firebase_admin.initialize_app(cred, name=name)
        else:
            firebase_admin.initialize_app(cred)

        # Store configuration
        self.credentials_path = credentials_path
        self.root = firestore.client()

    def get_event(self, event_id: str) -> Dict:
        # Construct ref
        ref = self.root.collection(u"events").document(event_id)
        log.debug(f"Created reference: {ref}")

        # Attempt get
        return ref.get().to_dict()

    def upload_event(self, event_details: Dict) -> str:
        # Get key
        key = event_details.pop("key")

        # Check for exists
        if self.get_event(key):
            raise KeyError(f"An event with key {key} already exists.")

        # Construct ref
        ref = self.root.collection(u"events").document(key)
        log.debug(f"Created reference: {ref}")

        # Add created timestamp
        event_details[u"created_datetime"] = firestore.SERVER_TIMESTAMP

        # Attempt set
        return ref.set(event_details)

    def upload_error(self, error: Dict) -> str:
        # Create error key
        # Just use the current datetime
        current_dt = str(datetime.utcnow()).replace(" ", "T")

        # Construct ref
        ref = self.root.collection(u"errors").document(current_dt)
        log.debug(f"Created reference: {ref}")

        # Attempt set
        return ref.set(error)

    def get_indexed_words(self) -> Dict[str, Dict]:
        """
        Get all preprocessed words.
        """

        return {}

    def upload_indexed_words(self, words: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Provided a dictionary of dictionaries with {word: {indexing results}} update or add index results for each one.
        """

        return {}

    def get_transcript(self, transcript_id: str) -> str:
        """
        Get a transcript from the transcript id.
        """
        # Construct ref
        ref = self.root.collection(u"transcripts").document(transcript_id)
        log.debug(f"Created reference: {ref}")

        # Attempt get
        return ref.get().to_dict()

    def upload_transcript(self, transcript_details: Dict) -> str:
        """
        Upload a transcript and return the transcript id.
        """
        # Get key
        key = transcript_details.pop("key")

        # Check for exists
        if self.get_transcript(key):
            raise KeyError(f"A transcript with key {key} already exists.")

        # Construct ref
        ref = self.root.collection(u"transcripts").document(key)
        log.debug(f"Created reference: {ref}")

        # Add created timestamp
        transcript_details[u"created_datetime"] = firestore.SERVER_TIMESTAMP

        # Attempt set
        return ref.set(transcript_details)

    def __str__(self):
        return f"<FirebaseDatabase [{self.credentials_path}]>"

    def __repr__(self):
        return str(self)
