#pragma once

#include <string>
#include <vector>

#include "cinn/ir/ir.h"
#include "cinn/lang/compute.h"
#include "cinn/poly/stage.h"

namespace cinn {
namespace hlir {
namespace pe {

void ScheduleInjectiveCPU(poly::Stage *stage, const std::vector<int> &output_shape, const common::Target &target);

void CudaScheduleMul(poly::StageMap stages,
                     ir::Tensor output,
                     const std::vector<int> &output_shape,
                     const common::Target &target);

void CudaScheduleConv(poly::StageMap stages,
                      ir::Tensor input_pad,
                      ir::Tensor kernel_dilation,
                      ir::Tensor output,
                      const common::Target &target);

void CudaScheduleInjective(poly::Stage *stage, const std::vector<int> &output_shape, const common::Target &target);

void CudaSplitSchedule(poly::Stage *stage, const std::vector<int> &output_shape);

}  // namespace pe
}  // namespace hlir
}  // namespace cinn
