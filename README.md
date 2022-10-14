# [Jesse Myrberg's personal website](https://storage.googleapis.com/jmyrberg/index.html)

This repository contains source code for my personal website.

![Website screenshot](/docs/screenshot.jpg)


## Solution

The website is hosted on Google Cloud Platform (GCP) with near zero costs by utilizing serverless backend functions and static website hosting for user interface (UI).

The main technical components include:

* Backend - Python + various libraries + [functions-framework-python](https://github.com/GoogleCloudPlatform/functions-framework-python)

* UI - Node.js + Vue + Vuetify


## Demo projects

The website and this repository contains several demo projects, which are briefly described in the following.

### Forecaster

* Time series forecasting tool that creates forecasts based on user's own dataset, focus being on simplicity and fast performance

* Utilizes Nixtla's AutoArima from [statsforecast library](https://github.com/Nixtla/statsforecast)

### Document Context Similarity

* Tool that calculates the similarity of two documents based on Finnish version of Google's BERT natural language model

* Provides serverless model inference by utilizing the [transformers library](https://github.com/huggingface/transformers)

### Food Recommender

* Web app that lists food options in a meaningful manner, allowing user to interact and share the list with others

* Main logic written in Vue.js, object storage is used for saved lists

### Finscraper

* Tool that fetches content from popular Finnish websites with spiders, and allows user to download scraped items into Excel or JSON

* Provides a serverless spider through [finscraper](https://github.com/jmyrberg/finscraper) - a library that I have developed

### Maximum Flows

* Tool that optimizes the flows of a network which the user can create in the web browser

* Utilizes [vue-konva](https://github.com/konvajs/vue-konva) for creating the network, and [Google OR-Tools](https://developers.google.com/optimization) for solving the optimization problem


## Repository structure

<pre>
.
├── .vscode/tasks.json: Development & deployment commands
├── functions/: Backend functions
├── scripts/: Helper scripts
├── ui/: UI components
</pre>


## Project installation, development & deployment

### Backend

* Install - Run [scripts/install-conda-env.sh](scripts/install-conda-env.sh)

* Development & Deployment - See [.vscode/tasks.json](.vscode/tasks.json)

### UI

* Install - Run `npm install` under [ui](./ui)

* Development & Deployment - See [.vscode/tasks.json](.vscode/tasks.json) / [ui/package.json](ui/package.json) and adjust them for your setup

---

Jesse Myrberg (jesse.myrberg@gmail.com)
