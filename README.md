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

### Kesakisa 2026

* Private summer competition app for players and hosts, including code-based login, team scores, daily tasks, direct messages, rules, and mouse-hunt tracking

* Uses a Vue + Vite static frontend and a small Cloud Functions API for signed sessions and shared game state


## Repository structure

<pre>
.
├── .vscode/tasks.json: Development & deployment commands
├── functions/: Backend functions
├── kesakisa/: Kesakisa 2026 app, API, assets, and deployment notes
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

### Kesakisa

* API local setup - Copy [kesakisa/api/.env.example](kesakisa/api/.env.example) to `kesakisa/api/.env.local`, fill in random local values for `KESAKISA_CODE_SALT` and `KESAKISA_SESSION_SECRET`, install [kesakisa/api/requirements.txt](kesakisa/api/requirements.txt), and run the Functions Framework target `kesakisa_api`

* Web local setup - Run `npm install` under [kesakisa/web](kesakisa/web), then `npm run dev -- --port 5174`

* Deployment and release notes - See [kesakisa/RELEASE.md](kesakisa/RELEASE.md)

---

Jesse Myrberg (jesse.myrberg@gmail.com)
