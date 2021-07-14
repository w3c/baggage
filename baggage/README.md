# Baggage Header

Applications and libraries can use baggage to attach user-defined properties as part of a distributed request. A framework can automatically propagate this data to downstream services as part of the distributed context. The benefit of the cross-cutting nature of this context propagation means that it doesn't require any changes in the participating services (e.g., to change API signatures) to propagate these parameters. There are two main categories of use cases of baggage: 

1. Use cases that enable better _observability_ of the system.
2. Use cases that enable better _control_ of the system.

## Example use cases
The below are a few example use cases for baggage:

### Labeling synthetic traffic
Baggage can be used to tag synthetic requests, such as those from blackbox monitoring tools or load/stress testing tools, e.g. `isProduction=false`. This can help services distinguish between production requests and synthetic requests. For example, this can be used by a system to partition error rate metrics to have separate time series for production and synthetics. This can enable configuring alert thresholds independently for production and synthetics.

In addition, services can use baggage to customize behavior for synthetic requests. For example, a service can choose to redirect synthetic requests to a different cluster.

### Attributing resource usage to lines of business
Baggage can be used to attribute infrastructure spend to a line of business. While higher level services will likely have dedicated services for each line of business, lower layers such as storage or messaging might be shared across multiple lines of businesses. A client or an upstream service can use baggage to attach information on the line of business associated with that request, e.g. `lob=youtube`. Downstream services can use this to attribute operations (e.g., number of storage operations) to a specific line of business.

### Traffic prioritization / Quality of Service
Baggage can be used by services to prioritize requests to provide better QoS. In a system, there can be different types of requests with different priorities: e.g., in ride sharing app, request for making a trip is more important than adding a location to favorites. As this request propagates through the system, this information can be lost in the lower shared layers. To solve this, we can assign tiers to different requests and pass it as part of baggage. In case of a traffic spike, the services can prioritize based on it.

### Additional labels/annotations for Observability
An APM agent can _read_ baggage entries and use them to create additional attributes or annotations for a span or metric that is being recorded. Note that APM agents should not _write_ to baggage to store any correlation data. They should instead use the tracestate header defined in the [W3C TraceContext](https://github.com/w3c/trace-context/blob/main/spec/20-http_request_header_format.md) specification.

## HTTP Format
The HTTP format is defined [here](HTTP_HEADER_FORMAT.md) and the rationale is defined
[here](HTTP_HEADER_FORMAT_RATIONALE.md).

## Binary Format
TODO: add link here
