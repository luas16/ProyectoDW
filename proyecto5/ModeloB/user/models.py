from crum import get_current_request
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import model_to_dict
from django.views.generic import CreateView

from config.settings import MEDIA_URL, STATIC_URL


class User(AbstractUser):
    image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True)

    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def toJSON(self):
        item = model_to_dict(self, exclude=['password','user_permissions', 'last_login'])
        if self.last_login:
            item['last_login'] = self.last_login.strftime('%Y-%m-%d')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['image'] = self.get_image()
        item['full_name'] = self.get_full_name()
        item['groups'] = [{'id': g.id, 'name': g.name} for g in self.groups.all()]
        return item
    # metodo para comprobar el numero de grupo del usuario, estableciendo el primer
    # grupo por defecto
    def get_group_session(self):
        try:
            # obtengo los datos de la sesion actual
            request = get_current_request()
            #guardo los grupos del usuario activo
            groups = self.groups.all()
            #condiciono si tiene grupos
            if groups.exists():
                #si el no hay ningun grupo en la sesion activa
                if 'group' not in request.session:
                    #se establece el grupo 1 a la sesion activa
                    request.session['group'] = groups[0]
        except:
            pass
