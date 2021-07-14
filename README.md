# Baggage Specification

This repository is associated with the [baggage](https://w3c.github.io/baggage/) specification.

Status of the report is
[First Public Working Draft](https://www.w3.org/2017/Process-20170301/#first-wd).

See rationale
[document](baggage/HTTP_HEADER_FORMAT_RATIONALE.md) for
clarifications.

## Team Communication

See
[communication](https://github.com/w3c/distributed-tracing-wg#team-communication)

We appreciate feedback and contributions. Please make sure to read
rationale documents when you have a question about particular decision
made in specification.

## Goal

This specification defines propagation of baggage for events correlation
beyond the request identification that is covered by [trace
context](https://w3c.github.io/trace-context/) specification. Our goal
is to share this with the community so that various tracing and
diagnostics products can operate together.

## Reference Implementations

OpenTelemetry provides a reference implementation of the baggage specification. You can find details at [OpenTelemetry API](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/baggage/api.md). OpenTelemetry SDK ships a BaggagePropagator and enables it by default. For example, the .NET version of it is [here](https://github.com/open-telemetry/opentelemetry-dotnet/blob/5ddf9a486e755c53ab73debf87286a934fcbbb51/src/OpenTelemetry.Api/Context/Propagation/BaggagePropagator.cs) and it is documented [here](https://github.com/open-telemetry/opentelemetry-dotnet/blob/main/src/OpenTelemetry.Api/README.md#baggage-api).

Another system that supports the baggage concept is .NET. It supports it as part of the [System.Diagnostics.Activity class](https://github.com/dotnet/corefx/blob/master/src/System.Diagnostics.DiagnosticSource/src/System/Diagnostics/Activity.cs) and it is documented [here](https://docs.microsoft.com/en-us/dotnet/api/system.diagnostics.activity?view=net-5.0). However, it is not a strict reference implementation: for example, it doesn't enforce the same character set or limits.

## Why are we doing this

See
[Why](https://github.com/w3c/distributed-tracing-wg#why-are-we-doing-this)

## Contributing

See [Contributing.md](CONTRIBUTING.md) for details.
