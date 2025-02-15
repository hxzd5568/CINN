# Copyright (c) 2022 CINN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright (c) 2022 CINN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import numpy as np
from op_test import OpTest, OpTestTool
import paddle
import cinn
from cinn.frontend import *
from cinn.common import *
import logging
import os

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper())
logger = logging.getLogger(name="index_select")


@OpTestTool.skip_if(not is_compiled_with_cuda(),
                    "x86 test will be skipped due to timeout.")
class TestIndexSelectOp(OpTest):
    def setUp(self):
        self.init_case()

    def init_case(self):
        self.inputs = {
            "x":
            np.array([[[1.1, 1.2, 1.3], [2.1, 2.2, 2.3], [3.1, 3.2, 3.3],
                       [4.1, 4.2, 4.3]],
                      [[5.1, 5.2, 5.3], [6.1, 6.2, 6.3], [7.1, 7.2, 7.3],
                       [8.1, 8.2, 8.3]],
                      [[9.1, 9.2, 9.3], [10.1, 10.2, 10.3], [11.1, 11.2, 11.3],
                       [12.1, 12.2, 12.3]]]).astype("float32"),
            "index":
            np.array([0, 0, 2, 2]).astype("int32")
        }
        self.axis = 0

    def build_paddle_program(self, target):
        x = paddle.to_tensor(self.inputs["x"], stop_gradient=True)
        index = paddle.to_tensor(self.inputs["index"], stop_gradient=True)
        out = paddle.index_select(x, index, self.axis)
        logger.debug(" -- The output of Paddle:\n{}".format(out))
        self.paddle_outputs = [out]

    def build_cinn_program(self, target):
        builder = CinnBuilder("index_select")
        x = builder.create_input(Float(32), self.inputs["x"].shape, "x")
        index = builder.create_input(
            Int(32), self.inputs["index"].shape, "index")
        out = builder.index_select(x, index, axis=self.axis)

        prog = builder.build()
        res = self.get_cinn_output(prog, target, [x, index],
                                   [self.inputs["x"], self.inputs["index"]],
                                   [out])
        logger.debug(" -- The output of CINN:\n{}".format(res))
        self.cinn_outputs = res

    def test_check_results(self):
        self.check_outputs_and_grads()


class TestIndexSelectOpCase1(TestIndexSelectOp):
    def init_case(self):
        self.inputs = {
            "x": np.random.random([16, 32, 32]).astype("float32"),
            "index": np.random.randint(0, 16, 64).astype("int32")
        }
        self.axis = 0


class TestIndexSelectOpCase2(TestIndexSelectOp):
    def init_case(self):
        self.inputs = {
            "x": np.random.random([16, 32, 32]).astype("float32"),
            "index": np.random.randint(0, 32, 15).astype("int32")
        }
        self.axis = 1


class TestIndexSelectOpCase3(TestIndexSelectOp):
    def init_case(self):
        self.inputs = {
            "x": np.random.random([16, 16, 32, 32]).astype("float32"),
            "index": np.random.randint(0, 32, 8).astype("int32")
        }
        self.axis = 2


class TestIndexSelectOpCase4(TestIndexSelectOp):
    def init_case(self):
        self.inputs = {
            "x": np.random.random([17, 29, 31, 13]).astype("float32"),
            "index": np.random.randint(0, 13, 11).astype("int32")
        }
        self.axis = 3


class TestIndexSelectOpCase5(TestIndexSelectOp):
    def init_case(self):
        self.inputs = {
            "x": np.random.random([17, 29, 31, 17]).astype("float32"),
            "index": np.random.randint(0, 17, 3).astype("int32")
        }
        self.axis = -1


class TestIndexSelectOpCase6(TestIndexSelectOp):
    def init_case(self):
        self.inputs = {
            "x": np.random.random([17, 29, 31]).astype("float32"),
            "index": np.random.randint(0, 29, 9).astype("int32")
        }
        self.axis = -2


if __name__ == "__main__":
    unittest.main()
