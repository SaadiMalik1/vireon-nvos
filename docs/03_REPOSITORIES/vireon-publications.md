# vireon-publications

The goal of VIREON is to end the publication of static PDFs.

`vireon-publications` acts as a central registry mapping DOIs to executable scientific manifests. When an author publishes a paper utilizing VIREON, they submit their execution DAG to this repository's JSON registry. 

Peer reviewers can clone this repository, run `vireon reproduce 10.1038/...`, and the CLI will automatically parse the `doi_index.json`, fetch the required `vireon-corpus` datasets, and immediately generate the exact `IEvidence` bundle and statistical plots cited in the paper.