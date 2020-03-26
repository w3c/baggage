# Correlation Context HTTP Header Format

A correlation context header is used to pass the name-value context properties for the trace. This is a companion header for the `traceparent`. The values should be passed along to any child requests. Note that uniqueness of the key within the `Correlation-Context` is not guaranteed. Context received from upstream service may be altered before passing it along.

*See [rationale document](HTTP_HEADER_FORMAT_RATIONALE.md) for details of decisions made for this format.*

# Format

## Header name

`Correlation-Context`

## Header value

The header value contains a list of key/value pairs. The first pair MUST contain the version of the header
as `v=<version>`.

The header MAY be sent or received as multiple header fields. Multiple header fields MUST be handled as specified by <a data-cite='!RFC7230#field.order'>RFC7230 Section 3.2.2 Field Order</a>. The header SHOULD be sent as a single field when possible, but MAY be split into multiple header fields. When sending the header as multiple header fields, it MUST be split according to <a data-cite='!RFC7230#field.order'>RFC7230</a>. When receiving multiple header fields, they MUST be combined into a single header according to <a data-cite='!RFC7230#field.order'>RFC7230</a>.

When multiple headers are combined as described before, the resulting combined header will contain
a version identifier for each individual header that was concatinated. This is intended and parsers have to expect that after the first version identifier another version identifier might occur at any time marking subsequent key/value pairs compliant with the denoted version until another version identifier occurs.


This section uses the Augmented Backus-Naur Form (ABNF) notation of [[!RFC5234]], including the DIGIT rule in <a data-cite='!RFC5234#appendix-B.1'>appendix B.1 for RFC5234</a>. It also includes the `OWS` rule from <a data-cite='!RFC7230#whitespace'>RFC7230 section 3.2.3</a>.

The `DIGIT` rule defines numbers `0`-`9`.

The `OWS` rule defines an optional whitespace character. To improve readability, it is used where zero or more whitespace characters might appear.

The caller SHOULD generate the optional whitespace as a single space; otherwise, a caller SHOULD NOT generate optional whitespace. See details in the <a data-cite='!RFC7230#whitespace'>corresponding RFC</a>.

The field value is a `list` of `list-members` separated by commas (`,`). A `list-member` is a key/value pair separated by an equals sign (`=`). Spaces and horizontal tabs surrounding `list-member`s are ignored. There can be a maximum of 180 `list-member`s in a `list`.
One single key/value pair mut not be larger than `4096 Bytes`.
The total size of the header MUST not exceed `8192 Bytes`.

### list

A simple example of the header value might look like:

`v=0,key1=opaqueValue1[;properties1],key2=opaqueValue2[;properties2]`

@TODO: Provide ABNF once agreed upon

**Limits:**
1. Maximum number of name-value pairs: `180`.
2. Maximum number of bytes per a single name-value pair: `4096`.
3. Maximum total length of all name-value pairs: `8192`.

## Version
A key value pair `v=<version>` MUST be the first element of the list.
For this spec, the curent version is `0`.

When headers are concatinated, there might be more than one version identifier in a single header.
Parsers have to expect a new version identifier that denotes the version for all following key/value pairs.
@TODO: We phrased that at many places now - maybe come up with a once-and-for-all solution

## Key
Token according to [[RFC2616](https://tools.ietf.org/html/rfc2616)], [Section 2.2](https://tools.ietf.org/html/rfc2616#section-2.2)


## Value
The value is an opaque string containing up to 256 printable ASCII [[RFC0020](https://tools.ietf.org/html/rfc20)] characters (i.e., the range 0x20 to 0x7E) except comma (,) and (=). Note that this also excludes tabs, newlines, carriage returns, etc.
@TODO: Isn't there an existing definition as for token?

```
value    = 0*255(chr) nblk-chr
nblk-chr = %x21-2B / %x2D-3C / %x3E-7E
chr      = %x20 / nblk-chr.
```


## Properties

Properties are expected to be in a format of keys & key-value pairs `;` delimited list `;k1=v1;k2;k3=v3`. Some properties may be known to the library or platform processing the header. Such properties may effect how library or platform processes corresponding name-value pair. Properties unknown to the library or platform MUST be preserved if name and/or value wasn't modified by the library or platform.

Spaces are allowed between properties and before and after equal sign. Properties with spaces MUST be considered identical to properties with all spaces trimmed.

# Examples of HTTP headers

Single header:

```
Correlation-Context: v=0,userId=sergey,serverNode=DF:28,isProduction=false
```

Context might be split into multiple headers:

```
Correlation-Context: v=0,userId=sergey
Correlation-Context: v=1,serverNode=DF%3A28,isProduction=false
```

Context might be re-combined into a single header:

```
Correlation-Context: v=0,userId=sergey,v=1,serverNode=DF%3A28,isProduction=false
                        [    v0 Parser   ][              v1 Parser              ]
```

Values and names might begin and end with spaces:

```
Correlation-Context: v= 0, userId =   sergey
Correlation-Context: v = 0, serverNode = DF%3A28, isProduction = false
```

## Example use case

For example, if all of your data needs to be sent to a single node, you could propagate a property indicating that.
```
Correlation-Context: v=0,serverNode=DF:28
```

For example, if you need to log the original user ID when making transactions arbitrarily deep into a trace.
```
Correlation-Context: v=0,userId=sergey
```

For example, if you have non-production requests that flow through the same services as production requests.

```
Correlation-Context: v=0,isProduction=false
```
