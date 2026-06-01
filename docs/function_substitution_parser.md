# Function Substitution Parser

This document describes the notation rules used by the function substitution engine.

## Goals

- Keep the input syntax compact and readable.
- Allow different operations to share the same surface notation when the operand type makes the meaning unambiguous.
- Leave room for future configurable aliases without rewriting the parser pipeline.

## Current Notation

### Absolute-value bars

The parser accepts bar-delimited expressions such as `|x|` and normalizes them into a generic `bar(...)` node.

The runtime decides the exact meaning:

- scalar or complex input: absolute value
- vector or column input: norm
- matrix input: determinant

Examples:

```text
|x|      -> bar(x)
|v|      -> bar(v)
|A|      -> bar(A)
```

### Transpose marker

The parser accepts `B^t` and `B^{t}` as transpose notation.

Examples:

```text
B^t      -> transpose(B)
B^{t}    -> transpose(B)
```

## Validation

The parser does not decide whether a given operation is mathematically valid.
That decision is deferred to the type checker and validator, which can reject:

- determinants of non-square matrices
- transposes of non-matrix values
- operations that violate dimension or shape rules

## Extensibility

Future notation variants can be introduced through operation aliases and operation metadata.
The parser is intentionally thin so new surface syntax can be added without changing the evaluation model.
