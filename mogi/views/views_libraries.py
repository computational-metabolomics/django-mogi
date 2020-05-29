# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import tempfile
import os
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from mogi.models import models_libraries
from mogi.forms import forms_libraries

from mogi.tasks import upload_library



class LibrarySpectraSourceCreateView(LoginRequiredMixin, CreateView):
    model = models_libraries.LibrarySpectraSource
    form_class = forms_libraries.LibrarySpectraSourceForm

    success_url = '/misa/success'

    def form_valid(self, form):

        lsr = form.save(commit=False)
        msp = form.cleaned_data['msp']

        tdir = tempfile.mkdtemp()
        templib_pth = os.path.join(tdir, 'library.msp')
        with open(templib_pth, 'w') as f:
            for line in msp:
                f.write(line)

        result = upload_library.delay(templib_pth, lsr.name)
        self.request.session['result'] = result.id
        return render(self.request, 'gfiles/status.html', {'s': 0, 'progress': 0})
        # return render(request, 'dma/status.html', {'s': 0, 'progress': 0})


