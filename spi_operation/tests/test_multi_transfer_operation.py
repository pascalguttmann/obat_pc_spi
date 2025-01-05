import unittest

from bitarray import bitarray

from single_transfer_operation import SingleTransferOperation
from multi_transfer_operation import MultiTransferOperation


class TestMultiTransferOperation(unittest.TestCase):
    op_cmd_10_bit = bitarray("0001000100")
    op_rsp_10_bit = bitarray("1000100010")
    single_op = SingleTransferOperation(
        op_cmd_10_bit, op_rsp_10_bit, response_required=True
    )

    def test_eq(self):
        op = MultiTransferOperation([self.single_op])
        op_eq = MultiTransferOperation([self.single_op])
        op_neq = MultiTransferOperation([MultiTransferOperation([self.single_op])])
        self.assertIsNot(op, op_eq)
        self.assertEqual(op, op_eq)
        self.assertIsNot(op, op_neq)
        self.assertNotEqual(op, op_neq)
