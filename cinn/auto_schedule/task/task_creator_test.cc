// Copyright (c) 2022 CINN Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "cinn/auto_schedule/task/task_creator.h"

#include <gtest/gtest.h>

#include <memory>
#include <vector>

#include "cinn/common/target.h"
#include "cinn/frontend/net_builder.h"
#include "cinn/frontend/syntax.h"
#include "cinn/hlir/framework/graph.h"
#include "cinn/hlir/framework/graph_compiler.h"
#include "cinn/hlir/framework/node.h"

namespace cinn {
namespace auto_schedule {

using ::cinn::frontend::NetBuilder;
using ::cinn::frontend::Program;
using ::cinn::hlir::framework::Node;

Program CreateAddProgram() {
  constexpr int M = 32;
  constexpr int N = 24;

  NetBuilder builder("net_builder");
  auto a       = builder.CreateInput(Float(32), {M, N}, "A");
  auto b       = builder.CreateInput(Float(32), {M, N}, "B");
  auto c       = builder.Add(a, b);
  auto d       = builder.Add(a, c);
  auto program = builder.Build();

  return program;
}

TEST(TaskCreator, Basic) {
#ifdef CINN_WITH_CUDA
  Target target = common::DefaultNVGPUTarget();
#else
  Target target = common::DefaultHostTarget();
#endif
  Program prog = CreateAddProgram();
  auto graph   = std::make_shared<hlir::framework::Graph>(prog, target);

  TaskCreator task_creator;
  std::vector<TuneTask> tasks = task_creator.CreateTuneTaskOpLevel(graph.get());

  ASSERT_EQ(tasks.size(), 2UL);
  for (TuneTask& task : tasks) {
    std::vector<std::vector<Node*>>& task_graph = task.task_graph;
    ASSERT_EQ(task_graph.size(), 1UL);
    ASSERT_EQ(task_graph[0].size(), 1UL);
    ASSERT_EQ(task_graph[0][0]->op()->name, "elementwise_add");
  }
}

}  // namespace auto_schedule
}  // namespace cinn
