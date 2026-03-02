# Technical Appraoch 

To build a better claims finder system, I used a semantic search approach using text embeddings. Since the primary issue is that specific keyword matching is unreliable, semantic embeddings are able to find the closest matches and filter out unrelated claims. I chose to use semantic embeddings because they are perfectly suited for this task; they can measure the underlying meaning of text. 

# AI opportunities

I believe it would be helpful to build an AI agent that is specliazed to analyze insurance claims. This AI agent would be able to summarize long files, extract key factors, and situation specifics in order to reduce the workload of the adjuster. 

# Limitations & Next Steps

The biggest limitations of Hyperion is that it cannot scale super well in its current state and that it only can filter by jurisdiction and policy type. Future work could include adding more filters to narrow search results and overhauling the embedding calculations. Like above, an AI agent would also be helpful. Creating a feedback system would also be necessary to improve the model over time and improve the user trust. Containerizing and deploying Hyperion to the cloud would also be a good next step to make it more accessible. 

# Scaling Considerations

Currently, Hyperion can reasonably handle up to a few thousand claims without serious runtime issues because it uses a brute force appraoch to calculate embeddings. However, this is not scalable and would take hours for larger datasets. It should also use batch-processing to improve performance and protect against both memory errors and crashes. The searching mechanism could also be improved by using clustering, HNSW, or other approximate nearest neighbor (ANN) algorithms - we almost never need to look at all claims