# Baggage Header Format Rationale

This document provides a rationale for the decisions made for the `baggage` header format.

## General considerations

- It should be human-readable. Cryptic headers would hide the fact of potential information disclosure.
- It should be append-able (comma-separated) https://tools.ietf.org/html/rfc7230#page-24 so nodes
can add context properties without parsing existing headers.
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

Limits prevent processing, storage, and analysis of the header and its values from being overly burdensome. The overall size and number of list members is limited in order to place an upper limit on the costs incurred processing and storing the header and its constituent values.

Limiting the size of each key-value pair prevents any single value from exhausting the header size limit and preventing other values from being included. The maximum size of a key-value pair was chosen to allow a full URL to be stored with some additional metadata.
