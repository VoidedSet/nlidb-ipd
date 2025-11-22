from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated # Base permission
from .models import DatabaseConnection
from .serializers import DatabaseConnectionSerializer
from .db_utils import establish_connection, introspect_schema # Your utility functions

# NOTE: For now, we'll use IsAuthenticated. Later, we'll add a check for the ADMIN role.
class DatabaseConnectionViewSet(viewsets.ModelViewSet):
    """
    Allows Organization Admins to create, list, and test database connections.
    Access to this view is restricted to the current tenant's users.
    """
    serializer_class = DatabaseConnectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Queryset is automatically restricted to the current tenant's schema
        return DatabaseConnection.objects.all()

    @action(detail=True, methods=['post'], url_path='test')
    def test_connection(self, request, pk=None):
        """
        API endpoint to test the stored connection credentials and introspect schema.
        """
        connection_instance = self.get_object()
        
        try:
            # 1. Establish and test the connection
            engine = establish_connection(connection_instance)
            
            # 2. Introspect the client's external database schema
            schema_data = introspect_schema(engine) 
            
            # 3. Mark the connection as active and save
            connection_instance.is_active = True
            connection_instance.save()
            
            return Response({
                'status': 'success',
                'message': 'Connection successful. Credentials validated and schema introspected.',
                'tables_found': list(schema_data.keys()),
                'detail': f"Found {len(schema_data)} tables/views in client's database."
            }, status=status.HTTP_200_OK)
            
        except ConnectionError as e:
            # If the connection fails, mark it inactive
            connection_instance.is_active = False
            connection_instance.save()
            return Response({
                'status': 'error',
                'message': f"Connection failed: {str(e)}",
            }, status=status.HTTP_400_BAD_REQUEST)