from utils import *
from example_functions.fn_examples import *
from models.resource_type import *
from models.qos import Qos
from models.resource_unit import ResourceUnit

RESOURCE_SET = {
    ResourceType("edge_1", 1.0, 1.0, 6, 0),
    ResourceType("edge_2", 0.9, 1.5, 4, 0),
    ResourceType("cloud_1", 0.6, 3.0, 2, 0),
    ResourceType("cloud_2", 0.4, 5.0, 2, 0),
}


def predict_execution_time(f, qos, *params):
    # Takes function and its parameters as input (function: fi, parameters: p1, p2, p3, ... pn)

    # Model selection and prediction
    # 1: fi_model = identify_model(fi) # Identify correct ML model
    # 2: et_fi_base = fi_model.predict(p1, p2, ....., pn) # Predicted output time (estimated_time)
    et_fi_base = get_execution_time(f, *params)

    # print(f"\nEstimate Time To Execute: {round(et_fi_base, 5)} sec")

    # Estimate execution time for different resource types
    probable_list = estimate_hr_exec_time(et_fi_base)

    # Apply the User-specified QoS filter

    # The QoS filter details the QoS metrics such as time for completion, cost, preference of
    # execution etc.; it prunes the resource types and their associated
    # resource specifications that do not pass the QoS metrics for
    # that function.
    # 4: QoS_fi = fetchQoS(fi)

    # The candidate list holds the resource types and associated configurations in the order sorted by the QoS filter
    # 5: candidate_list = probable_list.applyFilter(QoS(fi))
    candidate_list = applyQosFilter(probable_list, qos)

    function_deployment(candidate_list, f, *params)
    return True


def estimate_hr_exec_time(et_fi_base: float) -> list[ResourceUnit]:
    # Returns a list of estimated execution costs and time for a function based on a reference execution time

    # rj: resource type
    # srj: resource specification

    # et_fi_rj: estimated computing time for the function with the resource type rj
    # psi (fi, rj , srj ): gives the conversion factor for function fi with resource type rj and resource specification of it being srj

    # ec_fi_rj: the estimated execution cost
    # omega (rj, srj): Cost function of the resource type rj

    probable_list = []

    # Time-cost Estimation Phase for different resource types
    for rj in RESOURCE_SET:
        # et_fi_rj = psi(fi, rj, srj) * et_fi_base
        et_fi_rj = rj.et_mul * et_fi_base
        # ec_fi_rj = omega(rj, srj) * et_fi_rj
        ec_fi_rj = rj.ec_mul * et_fi_rj
        # A tuple is formed and added to the probable
        # res_unit = (rj, srj, et_fi_rj, ec_fi_rj)
        res_unit = ResourceUnit(rj, et_fi_rj, ec_fi_rj)
        probable_list.append(res_unit)

    return probable_list


def function_deployment(candidate_list: list[ResourceUnit], f, *params):
    # Choose a worker for a function based on the candidate list, and deploy that function on it.

    # Selecting a suitable worker

    # 1: for rj in candidate_list:
    # 2:    resource_type = rj.get_resource_type()
    # 3:    for wk in resource_type:
    # The compatibility check considers the usable resource capacity in the worker, affinity of the data for the
    # function at the worker for making the choice.
    # 4:        if check_worker_for_compatibility(wk):
    # 5:            cw = wk
    # 6:            res_spec = rj
    # 7:            break
    # 8:        end if
    # 9:    end for
    # 10: end for

    for res_unit in candidate_list:
        res_type = res_unit.resourceType
        if res_type.check_worker_for_compatibility():
            res_type.add_worker_instance()
        # Dispatching the function execution
        # 11: cw.execute_function(fi, param_location, res_spec)
        execute_function(res_unit, f, *params)
        break

    return None


if __name__ == "__main__":
    predict_execution_time(
        fn_example_3,
        Qos(execution_cost=4, execution_time=1.15),
        "./img/image_1.jpeg",
    )

    predict_execution_time(
        fn_example_1,
        Qos(execution_cost=10, execution_time=2),
        2,
    )

    predict_execution_time(
        fn_example_2,
        Qos(execution_cost=6, execution_time=1),
        1,
    )

    predict_execution_time(
        fn_example_3,
        Qos(execution_cost=4, execution_time=1.15),
        "./img/image_2.jpeg",
    )
