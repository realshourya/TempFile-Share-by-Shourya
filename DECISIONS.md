# Architecture Decisions

## Temporary access
A cryptographically random token is used in each download URL. The physical storage filename is not exposed.

## Expiration
Every upload receives an `expires_at` timestamp 24 hours after upload. Downloads are rejected after that time.

## Cleanup
Expired database records and their corresponding local files are removed when the application handles requests.

## Access control
This version intentionally uses possession of the unguessable temporary URL as the access mechanism. Anyone with the valid link can download the file.

## Storage
Files are stored locally for this college/demo project. Production deployment should use dedicated object storage, HTTPS, rate limiting, malware scanning, and stronger upload restrictions.
