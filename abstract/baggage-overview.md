# Overview

The `baggage` header is used to propagate user-supplied key-value pairs and associated metadata through a distributed request.
These key-value pairs MAY be used for debugging, changing application behavior, communicating information about upstream services to downstream services, or other uses not listed here.
This specification does not define any particular header keys, values, or metadata, and it does not assign any specific meaning to the data being propagated.
A received header SHOULD be propagated to all downstream requests, though it MAY be altered to add, change, or remove any or all key-value pairs or metadata.
