import json
import os

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import FileForm
from .image import resize

UPLOAD_PATH = getattr(settings, 'AJAXIMAGE_DIR', 'ajaximage/')
AUTH_TEST = getattr(settings, 'AJAXIMAGE_AUTH_TEST', lambda u: u.is_staff)
FILENAME_NORMALIZER = getattr(settings, 'AJAXIMAGE_FILENAME_NORMALIZER', slugify)
ALLOW_IMAGE_TYPES = getattr(
    settings, 'AJAXIMAGE_ALLOW_IMAGE_TYPES',
    ('image/png', 'image/jpg', 'image/jpeg', 'image/pjpeg', 'image/gif', 'image/webp'))
BAD_IMAGE_TYPE_ERROR = getattr(settings, 'AJAXIMAGE_BAD_IMAGE_TYPE_ERROR', _('Bad image format.'))


@require_POST
@user_passes_test(AUTH_TEST)
def ajaximage(request, upload_to=None, max_width=None, max_height=None, crop=None, form_class=FileForm):
    form = form_class(request.POST, request.FILES)
    if form.is_valid():
        file_ = form.cleaned_data['file']

        if file_.content_type not in ALLOW_IMAGE_TYPES:
            data = json.dumps({'error': BAD_IMAGE_TYPE_ERROR})
            return HttpResponse(data, content_type='application/json', status=403)
        file_ = resize(file_, max_width, max_height, crop)
        file_name, extension = os.path.splitext(file_.name)
        safe_name = '{0}{1}'.format(FILENAME_NORMALIZER(file_name), extension)
        target_path = str(upload_to or UPLOAD_PATH)
        name = target_path if '.' in target_path[-5:] else os.path.join(target_path, safe_name)
        path = default_storage.save(name, file_)
        url = default_storage.url(path)
        return HttpResponse(json.dumps({'url': url, 'filename': path}), content_type="application/json")
    return HttpResponse(status=403)
