# Baggage HTTP Header Format

The `baggage` header is used to propagate user-supplied key-value pairs through a distributed request.
A received header MAY be altered to change or add information and it SHOULD be passed on to all downstream requests.

Multiple `baggage` headers are allowed. Values can be combined in a single header according to [RFC 7230](https://tools.ietf.org/html/rfc7230#page-24).

## Header Name

Header name: `baggage`

In order to increase interoperability across multiple protocols and encourage successful integration,
implementations SHOULD keep the header name lowercase.

## Header Encoding

This header is a [[UTF-8]] encoded [[UNICODE]] string, however it uses only code points from the Basic Latin Unicode Block which are encoded identically in both Unicode and [[ASCII]].

## Header Content

This section uses the Augmented Backus-Naur Form (ABNF) notation of [[!RFC5234]].

### Definition

```ABNF
baggage-string         =  list-member 0*179( OWS "," OWS list-member )
list-member            =  key OWS "=" OWS value *( OWS ";" OWS property )
property               =  key OWS "=" OWS value
property               =/ key OWS
key                    =  token ; as defined in RFC 7230, Section 3.2.6
value                  =  *baggage-octet
baggage-octet          =  %x21 / %x23-2B / %x2D-3A / %x3C-5B / %x5D-7E
                          ; US-ASCII characters excluding CTLs,
                          ; whitespace, DQUOTE, comma, semicolon,
                          ; and backslash
OWS                    =  *( SP / HTAB ) ; optional white space, as defined in RFC 7230, Section 3.2.3
```

`token` is defined in [[RFC7230]], Section 3.2.6: https://tools.ietf.org/html/rfc7230#section-3.2.6

The definition of `OWS` is taken from [[RFC7230]], Section 3.2.3: https://tools.ietf.org/html/rfc7230#section-3.2.3

#### baggage-string

List of `list-member`s with optional properties attached.
Uniqueness of keys between multiple `list-member`s in a `baggage-string` is not guaranteed.
The order of duplicate entries SHOULD be preserved when mutating the list.
Producers SHOULD try to produce a `baggage-string` without any `list-member`s which duplicate the `key` of another list member.

#### key

A `token` which identifies a `value` in the `baggage`. `token` is defined in [RFC7230, Section 3.2.6](https://tools.ietf.org/html/rfc7230#section-3.2.6).
Leading and trailing whitespaces (`OWS`) are allowed and are not considered to be a part of the key.

<aside class="note">

Though the baggage header is a [[UTF-8]] encoded [[UNICODE]] string, `key` is limited to the [=ASCII code points=] allowed by the definition of token in [[RFC7230]]. This is due to the implementation details of stable implementations prior to the writing of this specification. 

</aside>

#### value

A string which contains a value identified by the `key`.
Any code points outside of the `baggage-octet` range MUST be percent-encoded.
The percent code point (`U+0025`) MUST be percent-encoded.
Code points which are not required to be percent-encoded MAY be percent-encoded.
Percent-encoding is defined in [[RFC3986]], Section 2.1: https://datatracker.ietf.org/doc/html/rfc3986#section-2.1.

When decoding the value, percent-encoded octet sequences that do not match the UTF-8 encoding scheme MUST be replaced with the replacement code point (`U+FFFD`).

Leading and trailing whitespaces (`OWS`) are allowed and are not considered to be a part of the value.

Note, `value` MAY contain any number of the equal sign (`U+003D`) code points. Parsers
MUST NOT assume that the equal sign is only used to separate `key` and `value`.

<aside class="note">

Though the baggage header is a [[UTF-8]] encoded [[UNICODE]] string, `value` is limited to the [=ASCII code points=] of `baggage-octet`. This is due to the implementation details of stable implementations prior to the writing of this specification.

</aside>

#### property

Additional metadata MAY be appended to values in the form of property set, represented as semi-colon `;` delimited list of keys and/or key-value pairs, e.g. `;k1=v1;k2;k3=v3`. 
Property keys and values are given no specific meaning by this specification.
Leading and trailing `OWS` is allowed and is not considered to be a part of the property key or value.

### Limits

A platform MUST propagate all `list-member`s including any `list-member`s added by the platform whenever both of these conditions are met:

- **Condition 1:** The resulting `baggage-string` contains 64 `list-member`s or less.
- **Condition 2:** The resulting `baggage-string` is of size 8192 bytes or less.

If either of the above conditions is not met, a platform MAY drop `list-member`s until both conditions are met.
The selection of which `list-member`s to drop and their order is unspecified and left to the implementer.
Note that the above limits are _minimum_ requirements to comply with the specification.
An implementor or platform MAY define higher limits and SHOULD propagate as much baggage information as is reasonable within their requirements.
If a platform cannot propagate all baggage, it MUST NOT propagate any partial `list-member`s.
If there are multiple `baggage` headers, all limits apply to the combination of all `baggage` headers and not each header individually.

### Example

The following example header contains 3 `list-member`s.
The `baggage-string` contained in the header contains 86 bytes.
82 bytes come from the `list-member`s and 4 bytes come from commas and optional whitespace.

```
baggage: key1=value1;property1;property2, key2 = value2, key3=value3; propertyKey=propertyValue
```

- `key1=value1;property1;property2`
  - 31 bytes
- `key2 = value2`
  - 13 bytes
- `key3=value3; propertyKey=propertyValue`
  - 38 bytes

## Examples of HTTP headers

Assume we want to propagate these entries: `userId="alice"`, `serverNode="DF 28"`, `isProduction=false`,

Single header:

```
baggage: userId=alice,serverNode=DF%2028,isProduction=false
```

Here is one more example where values with characters outside of the `baggage-octet` range are percent-encoded. Consider the entry: `userId="Amélie"`, `serverNode="DF 28"`, `isProduction=false`:

```
baggage: userId=Am%C3%A9lie,serverNode=DF%2028,isProduction=false
```

Baggage might be split into multiple headers:

```
baggage: userId=alice
baggage: serverNode=DF%2028,isProduction=false
```

Values and names might begin and end with spaces:

```
baggage: userId =   alice
baggage: serverNode = DF%2028, isProduction = false
```

### Example use case

For example, if all of your data needs to be sent to a single node, you could propagate a property indicating that.

```
baggage: serverNode=DF%2028
```

For example, if you need to annotate logs with some request-specific information, you could propagate a property using the baggage header.

```
baggage: userId=alice
```

For example, if you have non-production requests that flow through the same services as production requests.

```
baggage: isProduction=false
```
# Mutating baggage
A system receiving a `baggage` request header SHOULD send it to outgoing requests.
A system MAY mutate the value of this header before passing it on.

Because baggage entry keys, values, and metadata are not specified here, producers and consumers MAY agree on any set of mutation rules that don't violate the specification. For example, keys may be deduplicated by keeping the first entry, keeping the last entry, or concatenating values together.

The following mutations are allowed:

* **Add a new key/value pair.** A key/value pair MAY be added.
* **Update an existing value.** The value for any given key MAY be updated.
* **Delete a key/value pair.** Any key/value pair MAY be deleted.
* **Deduplicating the list.** Duplicate keys MAY be removed.

If a system receiving or updating a `baggage` request header determines that the number of baggage entries exceeds the limit defined in the limits section above, it MAY drop or truncate certain baggage entries in any order chosen by the implementation.

If a system determines that the value of `baggage-string` is not in the format defined in this specification, the behavior is undefined. For example, it MAY remove an offending `list-member` before propagating the rest of the `baggage-string`, or MAY decide to not propagate the `baggage-string` at all. This specification is not specifying how implementation may decide which `list-member`s may be considered correct when the whole string is not a correct `baggage-string` as the specification does not prescribe any particular parsing algorithm.

Note, the `baggage-string` can be passed as multiple headers. Implementation is not providing any requirements to propagate those headers of many which are in correct format. The `baggage-string` is seen as a single value combined from multiple headers in this specification.