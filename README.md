# Introduction

> **Manga Review** is a _RESTful API_ built upon the _Django-REST Framework_ for creating and retrieving reviews for Manga series.

# Documentation and examples

Complete documentation, along with collection of examples, can be found [here](https://documenter.getpostman.com/view/17469158/UVyn2eGa).

# Overview

- Each Manga series has its own list of reviews and each review can be _liked_ by authenticated users.
- A series' rating is _automatically_ generated based on the rating and the number of likes of its own reviews.
- A user cannot like a review more than once.
- Reviews can only be modified or deleted by _their creators_.
- Authentication is needed for every `PUT`, `POST` and `DELETE` method.
- Authentication is also needed for retrieving (`GET`) users list.

# Complexity

- Nested serializers.
- Custom authentication per action.

# Models

## Series

- title\* `string`
- author\* `string`
- rating `read-only`
- genre\* `array of strings`
- year\* `integer between 1900 and [CURRENT YEAR]`
- about\* `string`
- completed\* `boolean`
- anime\* `boolean`
- chapters `integer`
- volumes `integer`
- official_translation\* `boolean`

\* stands for required fields

```
GENRES = ["shonen", "shojo", "seinen", "romance", "sports", "action", "adventure", "comedy", "drama", "slice of life", "fantasy", "horror", "psychological", "mecha", "historical", "cyberpunk"]
```

## Reviews

- reviewer `read-only User instance`
- content\* `string`
- rating\* `float between 0 and 10`
- likes `read-only User instances`
- date `read-only`
- series `read-only Series instance`

\* stands for required fields

# Authentication

Manga Review uses JWT authentication which works pretty much like Django-REST own token authentication but with a few handy perks.

- Each time User logs in, a new Token is retrieved.
- This Token is destroyed after 4 hours or when User logs out.
- This Token must be used for every `PUT`, `POST`, and `DELETE` actions.
- This Token is also required for one `GET` action: retrieving Users list.
- This Token shall be used send in the headers section like so: `Authentication: Token [TOKEN]`
