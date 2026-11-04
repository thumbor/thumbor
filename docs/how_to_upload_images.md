# How to upload Images

Thumbor provides a `/image` REST end-point to upload your images and manage it.

This way you can send thumbor your original images by doing a simple post to its
urls.

## Configuration

The table below show all configuration parameters to manage image upload:

| Configuration parameter | Default                       | Description                                                 |
| ----------------------- | ----------------------------- | ----------------------------------------------------------- |
| UPLOAD_ENABLED          | False                         | Indicates whether thumbor should enable File uploads        |
| UPLOAD_AUTH_REQUIRED    | False                         | Indicates whether POST, PUT and DELETE need a bearer token  |
| UPLOAD_AUTH_TOKENS      | []                            | Bearer tokens accepted when `UPLOAD_AUTH_REQUIRED` is True  |
| UPLOAD_PUT_ALLOWED      | False                         | Indicates whether image overwrite should be allowed         |
| UPLOAD_DELETE_ALLOWED   | False                         | Indicates whether image deletion should be allowed          |
| UPLOAD_PHOTO_STORAGE    | thumbor.storages.file_storage | The type of storage to store uploaded images with           |
| UPLOAD_DEFAULT_FILENAME | image                         | Default filename for image uploaded                         |
| UPLOAD_MAX_SIZE         | 0                             | Max size in bytes for images uploaded to thumbor            |
| MIN_WIDTH               | 1                             | Min width in pixels for images uploaded                     |
| MIN_HEIGHT              | 1                             | Min height in pixels for images uploaded                    |

Here, `file_storage` means `thumbor.storages.file_storage`.

Thumbor comes with the `/image` REST end-point to upload disabled by default. In
order to enable it, just set the `UPLOAD_ENABLED` configuration in your
thumbor.conf file to `True`.

Thumbor will then use the storage specified in the `UPLOAD_PHOTO_STORAGE`
configuration to save your images. You can use an existing storage (filesystem,
redis, mongo, hbase...) or
{doc}`create your own storage <create_my_own_storage>` if needed .

You can manage image putting and deletions simply set the configuration
parameters `UPLOAD_PUT_ALLOWED` and `UPLOAD_DELETE_ALLOWED` to `True`. This
parameters are set to `False` by default for security reasons.

Finally the upload constraints (max size, image width and height) will be
controlled by `UPLOAD_MAX_SIZE`, `MIN_WIDTH` and `MIN_HEIGHT` parameters.

(upload-authentication)=

## Authentication

By default, any client that reaches thumbor can upload images, and can replace
or delete them when `UPLOAD_PUT_ALLOWED` or `UPLOAD_DELETE_ALLOWED` are
enabled. thumbor logs a warning at startup when uploads are enabled without
authentication.

Set `UPLOAD_AUTH_REQUIRED` to `True` and list the accepted tokens in
`UPLOAD_AUTH_TOKENS` to require a bearer token on `POST`, `PUT` and `DELETE`
requests:

```python
import os

UPLOAD_ENABLED = True
UPLOAD_AUTH_REQUIRED = True
UPLOAD_AUTH_TOKENS = os.environ["UPLOAD_AUTH_TOKENS"].split(",")
```

Each token must be a non-empty ASCII string without whitespace, and thumbor
refuses to start when the list is empty or has an invalid token. Generate long
random tokens, for example with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Clients send the token in the `Authorization` header:

```
curl -i -H "Authorization: Bearer $UPLOAD_AUTH_TOKEN" \
    -H "Content-Type: image/jpeg" -XPOST http://thumbor-server/image \
    --data-binary "@tests/fixtures/images/20x20.jpg"
```

A request without a token, with another authentication scheme or with a token
that is not in the list gets `401 Unauthorized` with a `WWW-Authenticate`
header, before thumbor decodes or stores the image and before it checks
`UPLOAD_PUT_ALLOWED` and `UPLOAD_DELETE_ALLOWED`.

To rotate a token, add the new one to `UPLOAD_AUTH_TOKENS`, update the clients
and then remove the old one.

Keep in mind that:

- The token travels in clear text in every request, so expose the upload API
  only over HTTPS.
- Tokens are meant for server-to-server calls. Do not embed them in web pages
  or mobile apps, where anyone can read them.
- Every token can upload, replace and delete images. There are no per-token
  permissions.
- `GET` and `HEAD` requests to `/image/<id>` do not need a token. Uploaded
  images are also served by the regular imaging URLs, so authentication
  protects uploads and changes, not reads.
- thumbor receives the whole request body before it checks the token. Limit
  the request body size at your reverse proxy (for example with
  `client_max_body_size` in nginx) so unauthenticated clients cannot send
  large bodies.

## API Usage

The Thumbor `/image` REST end-point supports the commons
[HTTP methods](http://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol) :

- POST : to upload a new image
- GET : to display an image uploaded
- PUT : to replace an image uploaded by another preserving the URI
- DELETE : to remove an image uploaded from storage

By default, `PUT` and `DELETE` methods are disabled as explained above. This is
done to tighten thumbor's security.

### Posting

Posting is the only method allowed by default when you activate the upload
module. It allows new images to be sent to Thumbor.

In order to upload a new image, you have two choices:

- send an HTTP **POST** to the `/image` end-point with the image as payload
  (REST style)
- send an HTTP **POST** to the `/image` end-point with a multi-part form with a
  file field called media (Form style).

In the REST style mode you may add an optional `Slug` header to define the image
filename, which is useful for SEO reasons. As RFC 5023 defines it, the `Slug`
value is percent-encoded UTF-8, so `photo%20name.jpg` names the image
`photo name.jpg`. Not specifying a `Slug` causes the server to use the default
filename for the image (`UPLOAD_DEFAULT_FILENAME` parameter) .

The HTTP response will return a `Location` header pointing on the uploaded
image, with the filename percent-encoded. The URI presented in `Location`
header may be used to update or delete the image uploaded (see below).

For examples, see
{ref}`Upload an image via the REST API <upload-rest-api>` or
{ref}`Upload an image via a form <upload-form>`.

#### HTTP status code

The status code returned will be :

- 201 Created (success)
- 401 Unauthorized (authentication is required and the token is missing or
  invalid)
- 415 Unsupported Media Type (image type is not allowed)
- 412 Precondition Failed (image is too small or the file is not an image)

### Putting

Putting is a little more dangerous if you don't have strict control of who can
access the `/image` end-point. This is because whatever is sent using this
method gets saved to storage, overwriting the previous entry.

In order to replace an existing image, all you have to do is send an HTTP
**PUT** request to the `/image` end-point with the new image content as payload.
The new image will replace the original image preserving the URI.

As for the `POST` method you may add an optional `Slug` header to define the
image filename.

The HTTP response will return a `Location` header pointing on the modified
image. The URI presents in `Location` header may be used to update again the
image or delete it.

For an example, see {ref}`Modifying an image <modify-uploaded-image>`.

#### HTTP status code

The status code returned will be :

- 204 No Content (success)
- 401 Unauthorized (authentication is required and the token is missing or
  invalid)
- 405 Method Not Allowed (if thumbor's configuration disallows putting images)
- 415 Unsupported Media Type (image type is not allowed)
- 412 Precondition Failed (image is too small or file is not an image)

### Deleting

Deleting can be very dangerous, thus is disabled by default.

If you do enable it, in order to delete an image, all you have to do is send an
HTTP **DELETE** request to the `/image` end-point.

For an example, see {ref}`Deleting an image <delete-uploaded-image>`.

#### HTTP status code

- 204 No Content (success)
- 401 Unauthorized (authentication is required and the token is missing or
  invalid)
- 404 Not Found (image doesn't exists)
- 405 Method Not Allowed (if thumbor's configuration disallows deleting images)

## Example

Assuming the thumbor server is located at : `http://thumbor-server`

(upload-rest-api)=

### Upload an image via the REST API

When using the `/image` REST end-point to upload your image via the REST API :

```
curl -i -H "Content-Type: image/jpeg" -H "Slug: photo.jpg" \
    -XPOST http://thumbor-server/image \
    --data-binary "@tests/fixtures/images/20x20.jpg"
```

the HTTP **POST** request was send to the server :

```
POST /image
Content-Type: image/jpeg
Content-Length: 822
Slug : photo.jpg
```

and the Thumbor server should return:

```
HTTP/1.1 201 Created
Content-Length: 0
Content-Type: text/html; charset=UTF-8
Location: /image/05b2eda857314e559630c6f3334d818d/photo.jpg
Server: TornadoServer/2.1.1
```

The image is created at
`http://thumbor-server/image/05b2eda857314e559630c6f3334d818d/photo.jpg`. It can
be retrieved, modified or deleted via this URI.

The optional `Slug` HTTP header specifies the filename to use for the image
uploaded.

(upload-form)=

### Upload an image via a form

When using the `/image` REST end-point to upload your images via a form, the
user is free to choose the filename of the image via the `filename` field :

```
curl -i -XPOST http://thumbor-server/image \
    -F "media=@tests/fixtures/images/20x20.jpg;type=image/jpeg;filename=croco.jpg"
```

the HTTP **POST** request was send to the server :

```
POST /image
Content-Type: multipart/form-data; boundary=----------------------------11df125d8b12
Content-Length: 822
```

and the Thumbor server should return:

```
HTTP/1.1 201 Created
Content-Length: 0
Content-Type: text/html; charset=UTF-8
Location: /image/05b2eda857314e559630c6f3334d818d/croco.jpg
```

The image is created at
`http://thumbor-server/image/05b2eda857314e559630c6f3334d818d/croco.jpg`. It can
be retrieve, modify or delete via this URI using the REST API.

(modify-uploaded-image)=

### Modifying an image

To replace the previously uploaded image by another we use:

```
curl -i -H "Content-Type: image/jpeg" -H "Slug: modified_image.jpg" \
    -XPUT http://thumbor-server/image/05b2eda857314e559630c6f3334d818d/photo.jpg \
    --data-binary "@tests/fixtures/images/20x20.jpg"
```

the HTTP **PUT** request was send to the server :

```
PUT /image/05b2eda857314e559630c6f3334d818d/photo.jpg
Content-Type: image/jpeg
Content-Length: 822
Slug : modified_image.jpg
```

and the Thumbor server should return:

```
HTTP/1.1 204 No Content
Content-Length: 0
Content-Type: text/html; charset=UTF-8
Location: /image/05b2eda857314e559630c6f3334d818d/modified_image.jpg
Server: TornadoServer/2.1.1
```

(delete-uploaded-image)=

### Deleting an image

Finally to delete the uploaded image we use:

```
curl -i -XDELETE \
    http://thumbor-server/image/05b2eda857314e559630c6f3334d818d/modified_image.jpg
```

the HTTP **DELETE** request was send to the server :

```
DELETE /image/05b2eda857314e559630c6f3334d818d/modified_image.jpg
```

and the Thumbor server should return:

```
HTTP/1.1 204 No Content
Content-Length: 0
Content-Type: text/html; charset=UTF-8
Server: TornadoServer/2.1.1
```
