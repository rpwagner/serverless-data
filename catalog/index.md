# Serverless Image Data Repository

![Random Image](https://g-e77286.ca528.03c0.data.globus.org/public/unostentation-exhalation.png)

## Random Images

[Browse the catalog](catalog/)

The Serverless Image Data Repository contains datasets of
randomly-generated images.

## Data Access

This repository demonstrates how to host dataset files on Globus collections while
providing a publicly available site for data discovery. The site is
hosted using [GitHub Pages](https://pages.github.com) a free service
that can deploy sites written in Markdown. Because the Globus
collection hosting the datasets provides HTTPS access, images from the
collection are embedded in catalog pages.

This site represents the catalog, with metadata about the catalog
itself and the datasets in the repository. The catalog is completely
public while the datasets are group in three levels of access:

- Public
- Accept Terms & Conditions
- Moderated Access

Public is completely public, including anonymous access via HTTPS. 

Accept Terms & Conditions means that a user must join the the [Serverless Data
Users](https://app.globus.org/groups/260da91f-3496-11ed-b941-972795fc9504/about)
Globus Group, provided they accept the terms & conditions. All Globus users
can join the Group without any actions by repository personnel. This is the “just sign
up” model where joining the Group provides a list of registered users.

Moderate Access means that the user can ask to join the [Serverless
Data Project
One](https://app.globus.org/groups/cf9d1f5b-3496-11ed-b941-972795fc9504/about)
Globus Group, but a group manager must approve members. This is the “request access” model.

An inspiration for this concept is the [X-ray Tomography Data
Bank](https://tomobank.readthedocs.io/). TomoBank uses a Globus
collection at Argonne to store files and publishes descriptions of its
datasets on [ReadTheDocs](https://readthedocs.org). Because the
dataset metadata is on Github in the [TomoBank
repo](https://github.com/tomography/tomobank), users can submit new
datasets through pull requests.
