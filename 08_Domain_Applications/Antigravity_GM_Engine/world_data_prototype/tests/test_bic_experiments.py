import unittest
from bic_experiments import factorial_2x2, tactical_evidence_protocol


class FactorialTests(unittest.TestCase):
    def test_main_and_interaction_contrasts(self):
        result = factorial_2x2({'00': [10], '10': [14], '01': [12], '11': [22]}, synthetic=True, mode='SYNTHETIC')
        self.assertEqual((result['factor_A'], result['factor_B'], result['interaction_difference_in_differences']), (7, 5, 6))
        self.assertEqual(result['status'], 'SYNTHETIC_ARITHMETIC_ONLY')

    def test_zero_and_additive(self):
        zero = factorial_2x2({key: [2, 2] for key in ('00', '10', '01', '11')}, synthetic=True, mode='SYNTHETIC')
        self.assertEqual(zero['factor_A'], 0)
        additive = factorial_2x2({'00': [10], '10': [14], '01': [12], '11': [16]}, synthetic=True, mode='SYNTHETIC')
        self.assertEqual(additive['interaction_difference_in_differences'], 0)

    def test_missing_cells_and_confounded_real_data(self):
        missing = factorial_2x2({'00': [10], '11': [22]}, synthetic=False, mode='FAST_SIM')
        self.assertEqual(missing['status'], 'NOT_CAUSALLY_IDENTIFIED')
        real = factorial_2x2({key: [2] for key in ('00', '10', '01', '11')}, synthetic=False, mode='FAST_SIM', confounders=['team-season'])
        self.assertEqual(real['status'], 'NOT_CAUSALLY_IDENTIFIED')
        self.assertIsNone(real['confidence_interval'])

    def test_bad_numbers_and_mode(self):
        with self.assertRaises(ValueError):
            factorial_2x2({'00': [float('nan')], '10': [1], '01': [1], '11': [1]}, synthetic=True, mode='SYNTHETIC')
        self.assertEqual(tactical_evidence_protocol('FAST_SIM')['status'], 'TACTICAL_EXECUTION_UNKNOWN')
        self.assertFalse(tactical_evidence_protocol('CPU_VS_CPU_3D')['live_action_authorized'])
