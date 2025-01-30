from typing import Dict, Any, List
import json
from jinja2 import Template
import re

class ClientGenerator:
    def __init__(self, spec: Dict[str, Any], package_name: str):
        self.spec = spec
        self.package_name = package_name
        
    def generate(self) -> str:
        """
        Generate Python client code from the OpenAPI specification
        """
        # Extract API information
        info = self.spec.get('info', {})
        title = info.get('title', 'API')
        version = info.get('version', '1.0.0')
        
        # Generate classes for schemas
        schemas = self._generate_schemas()
        
        # Generate API client methods
        methods = self._generate_methods()
        
        # Combine everything using the template
        return self._render_template(
            title=title,
            version=version,
            schemas=schemas,
            methods=methods
        )
        
    def _generate_schemas(self) -> List[str]:
        """
        Generate Pydantic models from schema definitions
        """
        schemas = []
        components = self.spec.get('components', {}).get('schemas', {})
        
        for name, schema in components.items():
            schema_code = self._generate_pydantic_model(name, schema)
            schemas.append(schema_code)
            
        return schemas
        
    def _generate_methods(self) -> List[str]:
        """
        Generate client methods for each API endpoint
        """
        methods = []
        paths = self.spec.get('paths', {})
        
        for path, operations in paths.items():
            for method, operation in operations.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    method_code = self._generate_method(
                        path, method, operation
                    )
                    methods.append(method_code)
                    
        return methods
        
    def _generate_pydantic_model(self, name: str, schema: Dict[str, Any]) -> str:
        """
        Generate a Pydantic model from a schema definition
        """
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        fields = []
        for prop_name, prop_schema in properties.items():
            field_type = self._get_python_type(prop_schema)
            optional = prop_name not in required
            field = f"    {prop_name}: {field_type}"
            if optional:
                field += " = None"
            fields.append(field)
            
        return f"""class {name}(BaseModel):
    \"\"\"
    {schema.get('description', '')}
    \"\"\"
{'    '.join(fields)}
"""
        
    def _generate_method(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """
        Generate a client method for an API endpoint
        """
        operation_id = operation.get('operationId', f"{method}_{path.replace('/', '_')}")
        parameters = operation.get('parameters', [])
        request_body = operation.get('requestBody', {})
        responses = operation.get('responses', {})
        
        # Generate method signature
        params = []
        for param in parameters:
            param_name = param['name']
            param_type = self._get_python_type(param.get('schema', {}))
            required = param.get('required', False)
            if not required:
                param_type = f"Optional[{param_type}]"
                params.append(f"{param_name}: {param_type} = None")
            else:
                params.append(f"{param_name}: {param_type}")
                
        if request_body:
            content_type = list(request_body.get('content', {}).keys())[0]
            schema = request_body['content'][content_type]['schema']
            body_type = self._get_python_type(schema)
            params.append(f"body: {body_type}")
            
        return f"""
    async def {operation_id}({', '.join(['self'] + params)}) -> Any:
        \"\"\"
        {operation.get('description', '')}
        \"\"\"
        url = f"{path}"
        method = "{method.upper()}"
        
        # Prepare request
        headers = {{"Content-Type": "application/json"}}
        params = {{}}
        
        response = await self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=body if 'body' in locals() else None
        )
        
        return response.json()
"""
        
    def _get_python_type(self, schema: Dict[str, Any]) -> str:
        """
        Convert OpenAPI types to Python types
        """
        type_mapping = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'List',
            'object': 'Dict[str, Any]'
        }
        
        schema_type = schema.get('type', 'object')
        if schema_type == 'array':
            items = schema.get('items', {})
            item_type = self._get_python_type(items)
            return f"List[{item_type}]"
        
        return type_mapping.get(schema_type, 'Any')
        
    def _render_template(self, **kwargs) -> str:
        """
        Render the client template with the generated code
        """
        template = """
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import aiohttp
import json

{% for schema in schemas %}
{{ schema }}
{% endfor %}

class {{ title }}Client:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self._client = aiohttp.ClientSession()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.close()
        
{% for method in methods %}
{{ method }}
{% endfor %}
"""
        template = Template(template)
        return template.render(**kwargs) 