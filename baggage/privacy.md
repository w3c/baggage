# Privacy Considerations

Requirements to propagate headers to downstream services, as well as storing values of these headers, open up potential privacy concerns.
Using proprietary ways of context propagation, vendors and application developers could always encode information that contains user identifiable data.
This standard makes it possible for systems to operate on a known, standardized header to restrict propagation of sensitive data in the baggage when crossing trust boundaries.

Systems MUST assess the risk of header abuse. This section provides some considerations and initial assessment of the risk associated with storing and propagating this header. Systems may choose to inspect and remove sensitive information from the fields before processing the received data. All mutations should, however, conform to the list of mutations defined in this specification.

## Privacy of the baggage header
The main purpose of this header is to provide additional system-specific information to other systems within the same trust-boundary.
The `baggage` header may contain any <a href="#opaque">opaque</a> value in any of the keys.
As such, the `baggage` header can contain user-identifiable data.
Systems MUST ensure that the `baggage` header does not leak beyond defined trust boundaries and they MUST ensure that the channel that is used to transport potentially user-identifiable data is secured.
