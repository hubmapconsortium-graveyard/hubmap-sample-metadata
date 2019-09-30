# hubmap-sample-metadata

This is a test bed for demonstrating how the HCA Metadata Standard and W3C PROV will be used in HuBMAP.

## Roadmap

Eventually, this will be renamed to `hubmap-metadata`, and it will become a tool that could be used either in development by Django management scripts, or in production by some API. It will take as input CSVs and a workflow name, and produce as output templated HCA-valid JSON describing entities and RDF relating the entities.

## Symbology

HuBMAP uses the HCA Metadata Standard's [five entity types](https://github.com/HumanCellAtlas/metadata-schema/blob/dc60b25010d0b82796b0cb256a120317343040d5/docs/structure.md#metadata-entity-model) for its own metadata,
but the HCA Standard does not provide a sufficiently flexible way of describing provenance.
For that, we are using [W3C PROV](https://www.w3.org/TR/2013/NOTE-prov-primer-20130430/#intuitive-overview-of-prov).

That said, the domain-specific symbology of HCA is easier to understand at a glance,
so we will use it in the workflow examples.
Here is a demonstration of how the two symbologies correspond:

![Compare HCA to PROV](hca-prov.svg?sanitize=true)

(All diagrams in this repo are editable with [draw.io](https://www.draw.io/), either on the web or with their desktop app.)

- We are not using the HCA's `Project` entity type.
- We are using only a fraction of the PROV vocabulary; In particular, for now, we are not using `Agent`.
- The two systems have different arrow direction conventions.
- In PROV, `used` relates both the Protocol and Tissue Section to the Process. Roles are distinguished by [`qualifiedUsage`](https://www.w3.org/TR/prov-o/#qualifiedUsage).
