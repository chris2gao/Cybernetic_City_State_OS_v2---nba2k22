学生提交：老师，既然内积可以衡量语义的对齐度，那我们直接让 Q 和 K 做点乘，然后用 softmax 选出最大概率不就行了吗？为什么还要除以根号 d_k？这不多此一举吗？

[SYSTEM DRAFT]
Teacher: Your intuition is geometrically correct but probabilistically flawed. When you multiply vectors in a high-dimensional space without scaling, the variance of the inner product expands linearly with the dimension d_k. Let's ask the underlying Z3 engine to calculate the variance of the dot product sum(q_i * k_i).
