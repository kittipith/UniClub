from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Count
from django.db.models.functions import Concat
from django.db.models import CharField, Value as V

from .models import *

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
# Create your views here.
