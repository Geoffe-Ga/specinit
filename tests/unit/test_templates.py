"""Tests for template selection."""

from specinit.generator.templates import TEMPLATES, TemplateSelector


class TestTemplateSelector:
    """Tests for TemplateSelector."""

    def test_select_react_fastapi_for_web(self):
        """Web platform with React should select react-fastapi template."""
        selector = TemplateSelector()

        template = selector.select(
            platforms=["web"],
            tech_stack={"frontend": ["react"], "backend": ["fastapi"]},
        )

        assert template["name"] == "React + FastAPI Web App"

    def test_select_nextjs_for_nextjs_tech(self):
        """Next.js tech stack should select nextjs template."""
        selector = TemplateSelector()

        template = selector.select(
            platforms=["web"],
            tech_stack={"frontend": ["nextjs", "react"], "backend": []},
        )

        assert template["name"] == "Next.js Web App"

    def test_select_python_cli_for_cli_platform(self):
        """CLI platform should select python-cli template."""
        selector = TemplateSelector()

        template = selector.select(
            platforms=["cli"],
            tech_stack={"frontend": [], "backend": ["python", "click"]},
        )

        assert template["name"] == "Python CLI Tool"

    def test_select_react_native_for_mobile(self):
        """iOS/Android platforms should select react-native template."""
        selector = TemplateSelector()

        template = selector.select(
            platforms=["ios", "android"],
            tech_stack={"frontend": ["react-native"], "backend": []},
        )

        assert template["name"] == "React Native Mobile App"

    def test_select_fastapi_only_for_api(self):
        """API platform with FastAPI should select fastapi-only template."""
        selector = TemplateSelector()

        template = selector.select(
            platforms=["api"],
            tech_stack={"frontend": [], "backend": ["fastapi"]},
        )

        assert template["name"] == "FastAPI Backend"

    def test_get_all_templates(self):
        """get_all_templates should return all available templates."""
        selector = TemplateSelector()

        templates = selector.get_all_templates()

        assert len(templates) == 5
        assert "react-fastapi" in templates
        assert "nextjs" in templates

    def test_get_template_by_id(self):
        """get_template should return specific template by ID."""
        selector = TemplateSelector()

        template = selector.get_template("python-cli")

        assert template is not None
        assert template["name"] == "Python CLI Tool"

    def test_get_nonexistent_template(self):
        """get_template should return None for unknown template ID."""
        selector = TemplateSelector()

        template = selector.get_template("nonexistent")

        assert template is None

    def test_all_templates_have_required_fields(self):
        """All templates should have required fields."""
        required_fields = ["name", "description", "platforms", "tech_stack", "directory_structure"]

        for template_id, template in TEMPLATES.items():
            for field in required_fields:
                assert field in template, f"Template {template_id} missing {field}"

    def test_all_templates_have_plan_directory(self):
        """All templates should include plan/ in directory structure."""
        for template_id, template in TEMPLATES.items():
            directories = template["directory_structure"]
            assert any("plan" in d for d in directories), f"Template {template_id} missing plan/"
