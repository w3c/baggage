# Baggage HTTP Header Format

The `baggage` header is used to propagate user-supplied key-value pairs through a distributed request.
A received header MAY be altered to change or add information and it MUST be passed on to all downstream requests.

Multiple `baggage` headers are allowed. Values can be combined in a single header according to [RFC 7230](https://tools.ietf.org/html/rfc7230#page-24).

*See [rationale document](HTTP_HEADER_FORMAT_RATIONALE.md) for details of decisions made for this format.*


# Header Name

Header name: `baggage`

In order to increase interoperability across multiple protocols and encourage successful integration,
implementations SHOULD keep the header name lowercase.

# Header Content

This section uses the Augmented Backus-Naur Form (ABNF) notation of [[!RFC5234]].

## Definition

```ABNF
list        =  list-member 0*179( OWS "," OWS list-member )
list-member =  key OWS "=" OWS value *( OWS ";" OWS property )
property    =  key OWS "=" OWS value
property    =/ key OWS
key         =  token ; as defined in RFC 2616, Section 2.2
value       =  %x21 / %x23-2B / %x2D-3A / %x3C-5B / %x5D-7E
               ; US-ASCII characters excluding CTLs,
               ; whitespace, DQUOTE, comma, semicolon,
               ; and backslash
OWS         =  *( SP / HTAB ) ; optional white space, as defined in RFC 7230, Section 3.2.3
```

`token` is defined in [[!RFC2616]], Section 2.2: https://tools.ietf.org/html/rfc2616#section-2.2

The definition of `OWS` is taken from [[RFC7230]], Section 3.2.3: https://tools.ietf.org/html/rfc7230#section-3.2.3

### list
List of key-value pairs with optional properties attached.
It can not be guaranteed that keys are unique.
Consumers MUST be able to handle duplicate keys while producers SHOULD try to deduplicate the list.

### key
ASCII string according to the `token` format, defined in [RFC2616, Section 2.2](https://tools.ietf.org/html/rfc2616#section-2.2).
Leading and trailing whitespaces (OWS) are allowed but MUST be trimmed when converting the header into a data structure.

### value
A value contains a URL encoded UTF-8 string.
Leading and trailing whitespaces (OWS) are allowed but MUST be trimmed when converting the header into a data structure.

### property
Additional metadata MAY be appended to values in the form of property set, represented as semi-colon `;` delimited list of keys and/or key-value pairs, e.g. `;k1=v1;k2;k3=v3`. The semantic of such properties is opaque to this specification.
Leading and trailing OWS is allowed but MUST be trimmed when converting the header into a data structure.

## Limits
1. Maximum number of name-value pairs: `180`.
2. Maximum number of bytes per a single name-value pair: `4096`.
3. Maximum total length of all name-value pairs: `8192`.

## Example
`key1=value1;property1;property2, key2 = value2, key3=value3; propertyKey=propertyValue`

# Examples of HTTP headers

Single header:

```
baggage: userId=alice,serverNode=DF:28,isProduction=false
```

Context might be split into multiple headers:

```
baggage: userId=alice
baggage: serverNode=DF%3A28,isProduction=false
```

Values and names might begin and end with spaces:

```
baggage: userId =   alice
baggage: serverNode = DF%3A28, isProduction = false
```

## Example use case

For example, if all of your data needs to be sent to a single node, you could propagate a property indicating that.
```
baggage: serverNode=DF:28
```

For example, if you need to log the original user ID when making transactions arbitrarily deep into a trace.
```
baggage: userId=alice
```

For example, if you have non-production requests that flow through the same services as production requests.
```
baggage: isProduction=false
```
