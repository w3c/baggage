# Baggage Header Format Rationale

This document provides a rationale for the decisions made for the `baggage` header format.

## General considerations

- It should be human-readable. Cryptic headers would hide the fact of potential information disclosure.
- It should be appendable (comma-separated) https://tools.ietf.org/html/rfc7230#page-24 so nodes
can add baggage properties without parsing existing headers.
- Keys are a single word in ASCII, and values should be a short string in UTF-8 or a derivative of a URL.

## Why a single header?

Another option would be to use prefixed headers, such as `trace-context-X`, where `X` is a propagated
field name. That could reduce the size of the data, particularly in http/2, where header
compression can apply.

Generally speaking, a `baggage` header may be split into multiple headers, and
compression may be at the same ballpark as repeating values are converted into a single value
in HPAC's dynamic collection. That said, there was no profiling made to make this decision.

The approach with multiple headers has the following problems:
- Name values limitation is much more pressing when the context name is used a part of a header
name.
- The comma-separated format similar to the proposed still needs to be supported in every individual header which makes parsing harder.
- A single header is more comfortable to configure for tracing by many app servers, and makes CORS whitelisting more straightforward.

## Why not Vary-style?

The [Vary](https://tools.ietf.org/html/rfc7231#section-7.1.4) approach is another alternative,
where a fixed header is used to enumerate the list of other headers that actually contain the data.
which could be used to accomplish the same. For example, `baggage: x-department; x-user-id;
ttl=1` could tell the propagation to look at and forward the parent ID header, but only to the
next hop. This has an advantage of HTTP header compression (hpack) and also weave-in with legacy
tracing headers.

Vary approach may be implemented as a new "header reference" value type `ref`.
`baggage: x-b3-parentid;type=ref;ttl=1` if proven needed.

## Trimming of spaces

The header should be human-readable and editable. Thus spaces are allowed before and after the comma, equal sign, and semicolon separators. It makes manual editing of headers less error-prone. It also allows better visual separation of fields when value modified manually.

## Why not use Structured Field Values for HTTP?

We had several discussions about using [Structured Field Values for HTTP](https://datatracker.ietf.org/doc/html/rfc8941) and finally decided to go with this explicit definition of encoding. The rationale is to reduce complexity as we only need a small subset of the functionality for Baggage. For example, the closest match to this in Structured Field Values format is a dictionary, but it allows many features that adds complexity to Baggage (e.g., recursive inner lists with items of different types). While it may be possible to specify various restrictions to "subtract" functionality from RFC 8941, we believe it will make things more complex as we will end up in a much worse place - neither adhering to RFC 8941 nor having a simple specification. Further, we are not tied only to HTTP. In the future, we will expand the specification to other protocols and we want to retain a simpler encoding scheme.

## Lowercase header name

In order to maximize the portability of the `baggage` header it is intentionally specified as a single lowercase word.
While HTTP header names are case-insensitive, the `baggage` header is meant to be propagated over other protocols that have
different constraints. Representing the header as a single lowercase word maximizes the use and reduces the chance of error
when using the header in non-HTTP scenarios.

## Case sensitivity of keys

There are few considerations why the names should be case sensitive:
- some keys may be a URL query string parameters which are case sensitive
- forcing lower case decreases readability of the names written in camel case

## Value format
While the semantics of header values are specific to the producer and consumer of a key/value pair, we
concluded that string values should be encoded at the producer and decoded at the consumer and that the specification should define a mechanism for that.

URL encoding is a low-overhead way to encode Unicode characters for non-Latin characters in the values. URL encoding keeps a single word in Latin unchanged and accessible.


## Limits

Lower limits ensure a minimum usefulness for users, while preventing processing, storage, and analysis of the header and its values from being overly burdensome.
The minimum overall size and number of list members is given so that a user may reliably determine if a header value will be propagated, even through a platform with limited resources.
