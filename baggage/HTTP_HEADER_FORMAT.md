# Baggage HTTP Header Format

The `baggage` header is used to propagate user-supplied key-value pairs through a distributed request.
A received header MAY be altered to change or add information and it SHOULD be passed on to all downstream requests.

Multiple `baggage` headers are allowed. Values can be combined in a single header according to [RFC 7230](https://tools.ietf.org/html/rfc7230#page-24).

## Header Name

Header name: `baggage`

In order to increase interoperability across multiple protocols and encourage successful integration,
implementations SHOULD keep the header name lowercase.

## Header Content

This section uses the Augmented Backus-Naur Form (ABNF) notation of [[!RFC5234]].

### Definition

```ABNF
baggage-string         =  list-member 0*179( OWS "," OWS list-member )
list-member            =  key OWS "=" OWS value *( OWS ";" OWS property )
property               =  key OWS "=" OWS value
property               =/ key OWS
value                  =  *baggage-octet
baggage-octet          =  %x21 / %x23-2B / %x2D-3A / %x3C-5B / %x5D-7E
                          ; US-ASCII characters excluding CTLs,
                          ; whitespace, DQUOTE, comma, semicolon,
                          ; and backslash
OWS                    =  *( SP / HTAB ) ; optional white space, as defined in RFC 7230, Section 3.2.3
```

`token` is defined in [[!RFC7230]], Section 3.2.6: https://tools.ietf.org/html/rfc7230#section-3.2.6

The definition of `OWS` is taken from [[RFC7230]], Section 3.2.3: https://tools.ietf.org/html/rfc7230#section-3.2.3

#### baggage-string

List of `list-member`s with optional properties attached.
Uniqueness of keys between multiple `list-member`s in a `baggage-string` is not guaranteed.
The order of duplicate entries SHOULD be preserved when mutating the list.
Producers SHOULD try to produce a `baggage-string` without any `list-member`s which duplicate the `key` of another list member.

#### key

```ABNF
key                    =  key-start
                       =/ key-start key-character
; TODO decide on key start characters. These come from JS and exist primarily to distinguish them from other source code syntax items like numbers, quotes, and operators.
key-start              =  unicode-letter
key-start              =/ "$"
key-start              =/ "_"
key-start              =/ "\" unicode-escape-sequence
key-character          =  key-start
key-character          =/ unicode-combining-mark
key-character          =/ unicode-digit
key-character          =/ unicode-connector-punctuation
; TODO define these
; From JS <ZWNJ> and <ZWJ> are format-control characters that are used to make necessary distinctions when forming words or phrases in certain languages. In ECMAScript source text, <ZWNJ> and <ZWJ> may also be used in an identifier after the first character.
key-character          =/ <ZWNJ>
key-character          =/ <ZWJ>
```

```
TODO remove everything below when it is translated to EBNF
EVERYTHING BELOW THIS LINE DIRECTLY LIFTED FROM JAVASCRIPT"
UnicodeLetter
    any character in the Unicode categories “Uppercase letter (Lu)”, “Lowercase letter (Ll)”, “Titlecase letter (Lt)”, “Modifier letter (Lm)”, “Other letter (Lo)”, or “Letter number (Nl)”.
UnicodeCombiningMark
    any character in the Unicode categories “Non-spacing mark (Mn)” or “Combining spacing mark (Mc)”
UnicodeDigit
    any character in the Unicode category “Decimal number (Nd)”
UnicodeConnectorPunctuation
    any character in the Unicode category “Connector punctuation (Pc)”
UnicodeEscapeSequence
    u HexDigit HexDigit HexDigit HexDigit
```

<!-- TODO: is the word `token` meaningful anymore? Should we define it? -->
A `token` which identifies a `value` in the `baggage`.
A key must start with a letter, `_`, `$`, or a unicode escape sequence prefixed by a `\`.
Leading and trailing whitespaces (`OWS`) are allowed and are not considered to be a part of the key.

#### value

A value contains a string whose character encoding MUST be UTF-8 [[Encoding]].
Any characters outside of the `baggage-octet` range of characters MUST be percent-encoded.
Characters which are not required to be percent-encoded MAY be percent-encoded.
Percent-encoding is defined in [[RFC3986]], Section 2.1: https://datatracker.ietf.org/doc/html/rfc3986#section-2.1.

When decoding the value, percent-encoded octet sequences that do not match the UTF-8 encoding scheme MUST be replaced with the replacement character (U+FFFD).

Leading and trailing whitespaces (`OWS`) are allowed and are not considered to be a part of the value.

Note, `value` MAY contain any number of the equal sign (`=`) characters. Parsers
MUST NOT assume that the equal sign is only used to separate `key` and `value`.

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

Here is one more example where values with characters outside of the `baggage-octet` range of characters are percent-encoded. Consider the entry: `userId="Amélie"`, `serverNode="DF 28"`, `isProduction=false`:

```
baggage: userId=Am%C3%A9lie,serverNode=DF%2028,isProduction=false
```

Context might be split into multiple headers:

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

If a system determines that the value of a baggage entry is not in the format defined in this specification, it MAY remove that entry before propagating the baggage header as part of outgoing requests.
