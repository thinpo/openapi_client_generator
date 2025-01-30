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
        title = info.get('title', 'API').replace('-', '').replace(' ', '')
        version = info.get('version', '1.0.0')
        
        # Generate classes for schemas
        schemas = self._generate_schemas()
        
        # Generate API client methods
        methods = self._generate_methods()
        
        # Get security schemes
        security_schemes = self._get_security_schemes()
        
        # Combine everything using the template
        return self._render_template(
            title=title,
            version=version,
            schemas=schemas,
            methods=methods,
            security_schemes=security_schemes
        )
        
    def _generate_schemas(self) -> List[str]:
        """
        Generate Pydantic models from schema definitions
        """
        schemas = []
        components = self.spec.get('components', {}).get('schemas', {})
        
        # First pass: Generate basic models
        for name, schema in components.items():
            if 'allOf' not in schema:
                schema_code = self._generate_pydantic_model(name, schema)
                schemas.append(schema_code)
        
        # Second pass: Generate models with inheritance
        for name, schema in components.items():
            if 'allOf' in schema:
                schema_code = self._generate_inherited_model(name, schema)
                schemas.append(schema_code)
                
        return schemas
        
    def _generate_methods(self) -> List[str]:
        """
        Generate client methods for each API endpoint
        """
        methods = []
        paths = self.spec.get('paths', {})
        
        for path, operations in paths.items():
            path_params = operations.get('parameters', [])
            
            for method, operation in operations.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    method_code = self._generate_method(
                        path, method, operation, path_params
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
{chr(10).join(fields)}
"""

    def _generate_inherited_model(self, name: str, schema: Dict[str, Any]) -> str:
        """
        Generate a Pydantic model that inherits from another model
        """
        all_of = schema.get('allOf', [])
        parent_ref = next((s.get('$ref', '').split('/')[-1] for s in all_of if '$ref' in s), None)
        additional_props = next((s.get('properties', {}) for s in all_of if 'properties' in s), {})
        required = next((s.get('required', []) for s in all_of if 'required' in s), [])
        
        fields = []
        for prop_name, prop_schema in additional_props.items():
            field_type = self._get_python_type(prop_schema)
            optional = prop_name not in required
            field = f"    {prop_name}: {field_type}"
            if optional:
                field += " = None"
            fields.append(field)
            
        return f"""class {name}({parent_ref}):
    \"\"\"
    {schema.get('description', '')}
    \"\"\"
{chr(10).join(fields)}
"""
        
    def _generate_method(self, path: str, method: str, operation: Dict[str, Any], path_params: List[Dict[str, Any]] = None) -> str:
        """
        Generate a client method for an API endpoint
        """
        operation_id = operation.get('operationId', f"{method}_{path.replace('/', '_')}")
        parameters = path_params or [] + operation.get('parameters', [])
        request_body = operation.get('requestBody', {})
        responses = operation.get('responses', {})
        security = operation.get('security', [])
        
        # Generate method signature
        params = []
        query_params = []
        path_param_names = []
        
        for param in parameters:
            param_name = param['name']
            param_type = self._get_python_type(param.get('schema', {}))
            required = param.get('required', False)
            
            if param.get('in') == 'path':
                path_param_names.append(param_name)
                if required:
                    params.append(f"{param_name}: {param_type}")
                else:
                    params.append(f"{param_name}: Optional[{param_type}] = None")
            elif param.get('in') == 'query':
                query_params.append(param_name)
                params.append(f"{param_name}: Optional[{param_type}] = None")
                
        if request_body:
            content_type = list(request_body.get('content', {}).keys())[0]
            schema = request_body['content'][content_type]['schema']
            body_type = self._get_python_type(schema)
            params.append(f"body: {body_type}")
            
        # Get response type
        success_response = next((responses[code] for code in ['200', '201'] if code in responses), None)
        return_type = 'Any'
        if success_response and 'content' in success_response:
            content = success_response['content']
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                return_type = self._get_python_type(schema)
            
        method_params = ', '.join(['self'] + params)
        url_params = {p: '{' + p + '}' for p in path_param_names}
        formatted_path = path.format(**url_params) if url_params else path
            
        return f"""
    async def {operation_id}({method_params}) -> {return_type}:
        \"\"\"
        {operation.get('description', '')}
        \"\"\"
        url = f"{formatted_path}"
        method = "{method.upper()}"
        
        # Prepare request
        headers = {{"Content-Type": "application/json"}}
        params = {{}}
        
        # Add query parameters
        {self._generate_query_params(query_params)}
        
        # Add security headers
        {self._generate_security_headers(security)}
        
        response = await self._client.request(
            method=method,
            url=self.base_url + url,
            headers=headers,
            params=params,
            json=body if 'body' in locals() else None
        )
        
        if response.status >= 400:
            error_data = await response.json()
            raise ApiError(response.status, error_data)
        
        if response.status != 204:  # No content
            return await response.json()
"""

    def _get_python_type(self, schema: Dict[str, Any]) -> str:
        """
        Convert OpenAPI types to Python types
        """
        if '$ref' in schema:
            return schema['$ref'].split('/')[-1]
            
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

    def _get_security_schemes(self) -> Dict[str, Dict[str, Any]]:
        """
        Get security schemes from the OpenAPI spec
        """
        return self.spec.get('components', {}).get('securitySchemes', {})

    def _generate_query_params(self, param_names: List[str]) -> str:
        """
        Generate code to add query parameters
        """
        if not param_names:
            return ""
            
        lines = []
        for param in param_names:
            lines.append(f"if {param} is not None:")
            lines.append(f"    params['{param}'] = {param}")
        return "\n        ".join(lines)

    def _generate_security_headers(self, security: List[Dict[str, List[str]]]) -> str:
        """
        Generate code to add security headers
        """
        if not security:
            return ""
            
        lines = []
        for scheme in security:
            for scheme_name in scheme:
                if scheme_name == 'bearerAuth':
                    lines.append('if self.api_key:')
                    lines.append('    headers["Authorization"] = f"Bearer {self.api_key}"')
                elif scheme_name == 'apiKeyAuth':
                    lines.append('if self.api_key:')
                    lines.append('    headers["X-API-Key"] = self.api_key')
        return "\n        ".join(lines)
        
    def _render_template(self, **kwargs) -> str:
        """
        Render the client template with the generated code
        """
        template = """
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import aiohttp
import json
from dataclasses import dataclass

@dataclass
class ApiError(Exception):
    status_code: int
    error_data: Dict[str, Any]

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