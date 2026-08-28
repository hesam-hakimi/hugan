Good catch. I agree with you.

In the current diagram, the cache lookup happens after semantic planning. This means we may already call Azure OpenAI before checking the cache, so we are losing part of the benefit of having the cache.

I think a better approach is to have two levels of cache. The first one can be before semantic planning for repeated or predefined questions, so if we already have a valid answer, we can avoid the LLM call. The second cache can stay after semantic planning and be used for reusing the semantic plan or result.

For the first cache, we don’t need the semantic-plan hash. We can use things like the user authorization scope, normalized question or template ID, registry and policy versions, data freshness, and output type.
