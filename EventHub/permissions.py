from rest_framework.permissions import BasePermission, SAFE_METHODS


# Permission : only admins can edit, the others can only read
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True # if GET or others safe HTTP methods
        return request.user and request.user.is_staff # if admin
    

# Permission : only admins or the owner can edit, others can only create
class IsOwnerOrAdminOrCreateOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True # anyone can create
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.username == request.user.username
    
# Permission : idem than before, but the attribute is modified to correspond to the 'Registration' model
class IsOwnerOrAdminOrCreateOnlyForRegistration(IsOwnerOrAdminOrCreateOnly):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user_id.username == request.user.username
