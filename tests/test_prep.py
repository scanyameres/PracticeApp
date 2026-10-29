import unittest

from practiceapp.prep import build_preparation_plan


class BuildPreparationPlanTests(unittest.TestCase):
    def test_role_title_selects_role_topics_and_questions(self) -> None:
        plan = build_preparation_plan("Product Manager")

        self.assertIn("Product strategy", plan.focus_areas)
        self.assertTrue(any("customer problem" in question.prompt for question in plan.questions))
        self.assertEqual(plan.role_title, "Product Manager")

    def test_job_description_surfaces_skills_and_adds_a_specific_prompt(self) -> None:
        plan = build_preparation_plan(
            "Data Analyst",
            "Use SQL and Python to build dashboards and communicate insights.",
            "Senior",
        )

        self.assertEqual(plan.focus_areas[:2], ("Python", "SQL"))
        self.assertIn("Python", plan.questions[0].prompt)
        self.assertEqual(plan.seniority, "Senior")
        self.assertLessEqual(len(plan.questions), 7)

    def test_unknown_role_gets_general_questions_and_blank_title_fallback(self) -> None:
        plan = build_preparation_plan("  ", "Be curious and work with a great team.")

        self.assertEqual(plan.role_title, "Your next role")
        self.assertIn("Role expertise", plan.focus_areas)
        self.assertTrue(any(question.category == "Behavioral" for question in plan.questions))


if __name__ == "__main__":
    unittest.main()
