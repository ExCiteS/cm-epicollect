from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIRequestFactory

from projects.tests.model_factories import ProjectF
from contributions.tests.model_factories import ObservationFactory
from categories.tests.model_factories import (
    CategoryFactory, TextFieldFactory, MultipleLookupFieldFactory,
    MultipleLookupValueFactory
)
from ..models import EpiCollectProject as EpiCollectProjectModel
from ..views import (
    EpiCollectProject, EpiCollectUploadView, EpiCollectDownloadView
)


class ProjectDescriptionViewTest(APITestCase):
    def test_project_form(self):
        project = ProjectF.create(**{'isprivate': False})
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        type1 = CategoryFactory.create(**{'project': project})
        TextFieldFactory(**{'category': type1})
        type2 = CategoryFactory.create(**{'project': project})
        TextFieldFactory(**{'category': type2})
        type3 = CategoryFactory.create(**{'project': project})
        TextFieldFactory(**{'category': type3})
        factory = APIRequestFactory()
        request = factory.get(
            reverse('geokey_epicollect:project_form', args=(project.id, )))

        view = EpiCollectProject.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)


class UploadDataTest(APITestCase):
    def test_upload_data(self):
        project = ProjectF.create(
            **{'isprivate': False, 'everyone_contributes': True}
        )
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        type1 = CategoryFactory.create(**{'project': project})
        field = TextFieldFactory(**{'category': type1})

        data = 'location_lat=51.5175205&location_lon=-0.1729205&location_acc=20&location_alt=&location_bearing=&category=' + str(type1.id) + '&' + field.key + '_' + str(field.category.id) + '=Westbourne+Park'

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '1')

    def test_upload_checkboxes(self):
        project = ProjectF.create(
            **{'isprivate': False, 'everyone_contributes': True}
        )
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        type1 = CategoryFactory.create(**{'project': project})
        field = MultipleLookupFieldFactory(**{'category': type1})
        val_1 = MultipleLookupValueFactory(**{'field': field})
        val_2 = MultipleLookupValueFactory(**{'field': field})

        data = 'location_lat=51.5175205&location_lon=-0.1729205&location_acc=20&location_alt=&location_bearing=&category=' + str(type1.id) + '&' + field.key + '_' + str(field.category.id) + '=' + str(val_1.id) + '%2c+' + str(val_2.id)

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '1')

    def test_upload_data_to_private_project(self):
        project = ProjectF.create()
        type1 = CategoryFactory.create(**{'project': project})
        field = TextFieldFactory(**{'category': type1})

        data = 'location_lat=51.5175205&location_lon=-0.1729205&location_acc=20&location_alt=&location_bearing=&category=' + str(type1.id) + '&' + field.key + '_' + str(field.category.id) + '=Westbourne+Park'

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:upload', kwargs={
            'project_id': project.id
        })
        request = factory.post(
            url + '?type=data',
            data,
            content_type='application/x-www-form-urlencoded'
        )

        view = EpiCollectUploadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '0')


class DownloadDataTest(APITestCase):
    def test_download_data(self):
        project = ProjectF.create(**{'isprivate': False})
        EpiCollectProjectModel.objects.create(project=project, enabled=True)
        ObservationFactory.create_batch(
            20, **{'project': project, 'attributes': {'key': 'value'}})

        factory = APIRequestFactory()
        url = reverse('geokey_epicollect:download', kwargs={
            'project_id': project.id
        })
        request = factory.get(url)
        view = EpiCollectDownloadView.as_view()
        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 200)
