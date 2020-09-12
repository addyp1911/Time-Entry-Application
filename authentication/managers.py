from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """A custom user manager for creating my user class """

    # creating user
    def create_user(self, email_or_username, password, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not email_or_username:
            raise ValueError('The email id or username must be set')
        user = self.model(identifier=email_or_username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    # creating super user
    def create_superuser(self, identifier, password, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(identifier, password, **extra_fields)
