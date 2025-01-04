import unittest

from bitarray import bitarray
from typing import Optional

from operation import SingleTransferOperation


class TestSingleTransferOperation(unittest.TestCase):
    op_cmd_10_bit = bitarray("0001000100")
    op_rsp_10_bit = bitarray("1000100010")
    op_rsp_8_bit = bitarray("00001111")

    def test_operation_init_001(self):
        op = SingleTransferOperation(self.op_cmd_10_bit)
        self.assertEqual(len(op), len(self.op_cmd_10_bit))
        self.assertEqual(op._command, self.op_cmd_10_bit)
        self.assertEqual(op._response, None)
        self.assertEqual(op._response_required, True)
        self.assertEqual(op.get_response_required(), True)

    def test_operation_init_002(self):
        op = SingleTransferOperation(self.op_cmd_10_bit, response_required=False)
        self.assertEqual(len(op), len(self.op_cmd_10_bit))
        self.assertEqual(op._command, self.op_cmd_10_bit)
        self.assertEqual(op._response, None)
        self.assertEqual(op._response_required, False)
        self.assertEqual(op.get_response_required(), False)

    def test_operation_init_004(self):
        op = SingleTransferOperation(
            self.op_cmd_10_bit, self.op_rsp_10_bit, response_required=True
        )
        self.assertEqual(len(op), len(self.op_cmd_10_bit))
        self.assertEqual(op._command, self.op_cmd_10_bit)
        self.assertEqual(op._response, self.op_rsp_10_bit)
        self.assertEqual(op._response_required, True)
        self.assertEqual(op.get_response_required(), True)

    def test_operation_init_005(self):
        try:
            op = SingleTransferOperation(
                self.op_cmd_10_bit, self.op_rsp_10_bit, response_required=False
            )
        except ValueError:
            return

        self.fail("ValueError not raised for response_required==False.")

    def test_operation_set_response_001(self):
        op = SingleTransferOperation(self.op_cmd_10_bit)
        try:
            op.set_response(self.op_rsp_8_bit)
        except ValueError:
            return

        self.fail("ValueError not raised for length mismatch.")

    def test_operation_set_response_002(self):
        op = SingleTransferOperation(self.op_cmd_10_bit, response_required=False)
        try:
            op.set_response(self.op_rsp_10_bit)
        except ValueError:
            return

        self.fail("ValueError not raised for response_required==False.")

    def test_operation_set_response_003(self):
        op = SingleTransferOperation(self.op_cmd_10_bit)
        op.set_response(self.op_rsp_10_bit)
        self.assertEqual(len(op), len(self.op_cmd_10_bit))
        self.assertEqual(op._command, self.op_cmd_10_bit)
        self.assertEqual(op._response, self.op_rsp_10_bit)
        self.assertEqual(op._response_required, True)

    def test_operation_get_command(self):
        op = SingleTransferOperation(self.op_cmd_10_bit)
        self.assertEqual(op.get_command(), self.op_cmd_10_bit)

    def test_operation_get_response_001(self):
        op = SingleTransferOperation(self.op_cmd_10_bit)
        self.assertEqual(op.get_response(), None)

    def test_operation_get_response_002(self):
        op = SingleTransferOperation(self.op_cmd_10_bit, self.op_rsp_10_bit)
        self.assertEqual(op.get_response(), self.op_rsp_10_bit)
