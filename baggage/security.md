# Security Considerations

Systems relying on the `baggage` headers should also follow all best practices for parsing potentially malicious data, including checking for header length and content of header values.
These practices help to avoid buffer overflow and HTML injection attacks.

## Information Exposure
As mentioned in the privacy section, information in `baggage` may carry information that can be considered sensitive.
Application owners should either ensure that no proprietary or confidential information is stored in `baggage`, or they should ensure that `baggage` isn't present in requests that cross trust-boundaries.


## Other Risks
Application owners need to make sure to test all code paths leading to the sending of the `baggage` header. For example, in single page browser applications, it is typical to make cross-origin requests. If one of these code paths leads to `baggage` headers being sent by cross-origin calls that are restricted using <a data-cite='FETCH#http-access-control-request-headers'>`Access-Control-Allow-Headers`</a> [[FETCH]], it may fail.
