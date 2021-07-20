# Overview

The `baggage` header represents user-defined baggage associated with a trace. Libraries and platforms SHOULD propagate this header.
The `baggage` header is used to propagate user-supplied key-value pairs through a distributed request.
A received header MAY be altered to change or add information and it SHOULD be propagated to all downstream requests.
