import tequila.simulators.simulator_api
from tequila.circuit import gates
from tequila.objective import VectorObjective, ExpectationValue
from tequila.objective.objective import Variable
from tequila.hamiltonian import paulis
from tequila.circuit.gradient import grad
from tequila import numpy as np
import numpy
import pytest
import tequila as tq
from tequila.simulators.simulator_api import simulate


def test_non_quantum():
    E = tq.VectorObjective()
    E += 1.0
    E = E + 2.0
    E *= 2.0
    E = E * 2.0
    E = 1.0 * E
    E -= 1.0
    E = 1.0 + E
    E = E.apply(lambda x: x/3.0)
    assert E() == 2.0*2.0*(1.0 + 2.0)/3.0

@pytest.mark.parametrize("backend", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_compilation(backend):
    U = gates.X(target=[0,1,2,3,4,5])
    for i in range(10):
        U += gates.Ry(angle=(i,), target=numpy.random.randint(0,5,1)[0])
    U += gates.CZ(0,1) + gates.CNOT(1,2) + gates.CZ(2,3) + gates.CNOT(3,4) + gates.CZ(5,6)
    H = paulis.X(0) + paulis.X(1) + paulis.X(2) + paulis.X(3) + paulis.X(4) + paulis.X(5)
    H += paulis.Z(0) + paulis.Z(1) + paulis.Z(2) + paulis.Z(3) + paulis.Z(4) + paulis.Z(5)
    E = ExpectationValue(H=H, U=U)

    randvals = numpy.random.uniform(0.0, 2.0, 10)
    variables = {(i,): randvals[i] for i in range(10)}
    e0 = simulate(E, variables=variables, backend=backend)

    E2 = E*E
    for i in range(99):
        E2 += E*E

    compiled = tq.compile(E2, variables=variables, backend=backend)
    e2 = compiled(variables=variables)
    assert(E2.count_expectationvalues(unique=True) == 1)
    assert(compiled.count_expectationvalues(unique=True) == 1)
    assert numpy.isclose(100*e0**2, e2)

### these 8 tests test add,mult,div, and power, with the expectationvalue on the left and right.

@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_l_addition(simulator, value=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = e1 + 1
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator) + 1.
    an1 = np.sin(angle1(variables=variables)) + 1.
    assert np.isclose(val, en1, atol=1.e-4)
    assert np.isclose(val, an1, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_r_addition(simulator, value=numpy.random.uniform(0.0, 2.0*numpy.pi, 1)[0]):
    angle1 = Variable(name="angle1")
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = 1 + e1
    val = simulate(added, variables=variables, backend=simulator)
    en1 = 1 + simulate(e1, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables)) + 1.
    assert np.isclose(val, en1, atol=1.e-4)
    assert np.isclose(val, an1, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_l_multiplication(simulator, value=numpy.random.uniform(0.0, 2.0*numpy.pi, 1)[0]):
    angle1 = Variable(name="angle1")
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = e1 * 2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = 2 * simulate(e1, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables)) * 2
    assert np.isclose(val, en1, atol=1.e-4)
    assert np.isclose(val, an1, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_r_multiplication(simulator, value=numpy.random.uniform(0.0, 2.0*numpy.pi, 1)[0]):
    angle1 = Variable(name="angle1")
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = 2 * e1
    val = simulate(added, variables=variables, backend=simulator)
    en1 = 2 * simulate(e1, variables=variables, backend=simulator)
    an1 = np.sin(value) * 2
    assert np.isclose(val, en1, atol=1.e-4)
    assert np.isclose(val, an1, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_l_division(simulator, value=numpy.random.uniform(0.0, 2.0*numpy.pi, 1)[0]):
    angle1 = Variable(name="angle1")
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = e1 / 2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator) / 2
    an1 = np.sin(value) / 2.
    assert np.isclose(val, en1, atol=1.e-4)
    assert np.isclose(val, an1, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_r_division(simulator, value=numpy.random.uniform(0.0, 2.0*numpy.pi, 1)[0]):
    angle1 = Variable(name="angle1")
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = 2 / e1
    val = simulate(added, variables=variables, backend=simulator)
    en1 = 2 / simulate(e1, variables=variables, backend=simulator)
    an1 = 2 / np.sin(value)
    assert np.isclose(val, en1, atol=1.e-4)
    assert np.isclose(val, an1, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_l_power(simulator, value=numpy.random.uniform(0.0, 2.0*numpy.pi, 1)[0]):
    angle1 = Variable(name="angle1")
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = e1 ** 2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator) ** 2
    an1 = np.sin(angle1(variables=variables)) ** 2.
    assert np.isclose(val, en1, atol=1.e-4)
    assert np.isclose(val, an1, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_r_power(simulator, value=numpy.random.uniform(0.0, 2.0*numpy.pi, 1)[0]):
    angle1 = Variable(name="angle1")
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = 2 ** e1
    val = simulate(added, variables=variables, backend=simulator)
    en1 = 2 ** simulate(e1, variables=variables, backend=simulator)
    an1 = 2. ** np.sin(angle1(variables=variables))
    assert np.isclose(val, en1, atol=1.e-4)
    assert np.isclose(val, an1, atol=1.e-4)


### these four tests test mutual operations. We skip minus cuz it's not needed.

@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_ex_addition(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                     value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    H2 = paulis.Y(qubit=qubit)
    U2 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle2)
    e2 = ExpectationValue(U=U2, H=H2)
    added = e1 + e2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    en2 = simulate(e2, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables))
    an2 = -np.sin(angle2(variables=variables))
    assert np.isclose(val, en1 + en2, atol=1.e-4)
    assert np.isclose(val, an1 + an2, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_ex_multiplication(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                           value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    H2 = paulis.Y(qubit=qubit)
    U2 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle2)
    e2 = ExpectationValue(U=U2, H=H2)
    added = e1 * e2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    en2 = simulate(e2, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables))
    an2 = -np.sin(angle2(variables=variables))
    assert np.isclose(val, en1 * en2, atol=1.e-4)
    assert np.isclose(val, an1 * an2, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_ex_division(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                     value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    H2 = paulis.Y(qubit=qubit)
    U2 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle2)
    e2 = ExpectationValue(U=U2, H=H2)
    added = e1 / e2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    en2 = simulate(e2, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables))
    an2 = -np.sin(angle2(variables=variables))
    assert np.isclose(val, en1 / en2, atol=1.e-4)
    assert np.isclose(val, an1 / an2, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_ex_power(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                  value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    H2 = paulis.Y(qubit=qubit)
    U2 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle2)
    e2 = ExpectationValue(U=U2, H=H2)
    added = e1 ** e2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    en2 = simulate(e2, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables))
    an2 = -np.sin(angle2(variables=variables))
    assert np.isclose(val, en1 ** en2, atol=1.e-4)
    assert np.isclose(val, an1 ** an2, atol=1.e-4)


### these four tests test the mixed VectorObjective,ExpectationValue operations to ensure propriety

@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_mixed_addition(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                        value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    H2 = paulis.Y(qubit=qubit)
    U2 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle2)
    e2 = ExpectationValue(U=U2, H=H2)
    added = e1 + e2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    en2 = simulate(e2, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables))
    an2 = -np.sin(angle2(variables=variables))
    assert np.isclose(val, en1 + en2, atol=1.e-4)
    assert np.isclose(val, float(an1 + an2), atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_mixed_multiplication(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                              value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    H2 = paulis.Y(qubit=qubit)
    U2 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle2)
    e2 = ExpectationValue(U=U2, H=H2)
    added = e1 * e2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    en2 = simulate(e2, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables))
    an2 = -np.sin(angle2(variables=variables))
    assert np.isclose(val, en1 * en2, atol=1.e-4)
    assert np.isclose(val, an1 * an2, atol=1.e-4)

@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_mixed_division(simulator, value1=(numpy.random.randint(10, 1000) / 1000.0 * (numpy.pi / 2.0)),
                        value2=(numpy.random.randint(10, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    H2 = paulis.Y(qubit=qubit)
    U2 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle2)
    e2 = ExpectationValue(U=U2, H=H2)
    added = e1 / e2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    en2 = simulate(e2, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables))
    an2 = -np.sin(angle2(variables=variables))
    assert np.isclose(val, en1 / en2, atol=1.e-4)
    assert np.isclose(val, an1 / an2, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_mixed_power(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                     value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H1 = paulis.X(qubit=qubit)
    U1 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    H2 = paulis.Y(qubit=qubit)
    U2 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle2)
    e2 = ExpectationValue(U=U2, H=H2)
    added = e1 ** e2
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    en2 = simulate(e2, variables=variables, backend=simulator)
    an1 = np.sin(angle1(variables=variables))
    an2 = -np.sin(angle2(variables=variables))
    assert np.isclose(val, en1 ** en2, atol=1.e-4)
    assert np.isclose(val, an1 ** an2, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
@pytest.mark.parametrize('op', [np.add, np.subtract, np.float_power, np.true_divide, np.multiply])
def test_heterogeneous_operations_l(simulator, op, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                                    value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H2 = paulis.X(qubit=qubit)
    U2 = gates.X(target=control) + gates.Ry(target=qubit, control=control, angle=angle2)
    e2 = ExpectationValue(U=U2, H=H2)
    added = VectorObjective(argsets=[[angle1, e2.args[0]]], transformations=[op])
    val = simulate(added, variables=variables, backend=simulator)
    en2 = simulate(e2, variables=variables, backend=simulator)
    an1 = angle1(variables=variables)
    an2 = np.sin(angle2(variables=variables))
    assert np.isclose(val, float(op(an1, en2)), atol=1.e-4)
    assert np.isclose(en2, an2, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
@pytest.mark.parametrize('op', [np.add, np.subtract, np.true_divide, np.multiply])
def test_heterogeneous_operations_r(simulator, op, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                                    value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    qubit = 0
    control = 1
    H1 = paulis.Y(qubit=qubit)
    U1 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = VectorObjective(argsets=[[e1.args[0], angle2]], transformations=[op])
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    an1 = -np.sin(angle1(variables=variables))
    an2 = angle2(variables=variables)
    assert np.isclose(val, float(op(en1, an2)), atol=1.e-4)
    assert np.isclose(en1, an1, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_heterogeneous_gradient_r_add(simulator):
    ### the reason we don't test float power here is that it keeps coming up NAN, because the argument is too small
    angle1 = Variable(name="angle1")
    value = numpy.random.randint(100, 1000) / 1000.0 * (numpy.pi / 2.0)
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.Y(qubit=qubit)
    U1 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = VectorObjective(argsets=[[e1.args[0], angle1]], transformations=[np.add])
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    an1 = -np.sin(angle1(variables=variables))
    anval = angle1(variables=variables)
    dO = grad(added, 'angle1')
    dE = grad(e1, 'angle1')
    deval = simulate(dE, variables=variables, backend=simulator)
    doval = simulate(dO, variables=variables, backend=simulator)
    dtrue = 1.0 + deval
    assert np.isclose(float(val), float(np.add(en1, anval)))
    assert np.isclose(en1, an1, atol=1.e-4)
    assert np.isclose(doval, dtrue, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_heterogeneous_gradient_r_mul(simulator):
    ### the reason we don't test float power here is that it keeps coming up NAN, because the argument is too small
    angle1 = Variable(name="angle1")
    value = (numpy.random.randint(100, 1000) / 1000.0 * (numpy.pi / 2.0))
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.Y(qubit=qubit)
    U1 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = VectorObjective(argsets=[[e1.args[0], angle1]], transformations=[np.multiply])
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    an1 = -np.sin(angle1(variables=variables))
    anval = angle1(variables=variables)
    dO = grad(added, 'angle1')
    dE = grad(e1, 'angle1')
    deval = simulate(dE, variables=variables, backend=simulator)
    doval = simulate(dO, variables=variables, backend=simulator)
    dtrue = deval * anval + en1
    assert np.isclose(float(val), float(np.multiply(en1, anval)))
    assert np.isclose(en1, an1, atol=1.e-4)
    assert np.isclose(doval, dtrue, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_heterogeneous_gradient_r_div(simulator):
    ### the reason we don't test float power here is that it keeps coming up NAN, because the argument is too small
    angle1 = Variable(name="angle1")
    value = (numpy.random.randint(100, 1000) / 1000.0 * (numpy.pi / 2.0))
    variables = {angle1: value}
    qubit = 0
    control = 1
    H1 = paulis.Y(qubit=qubit)
    U1 = gates.X(target=control) + gates.Rx(target=qubit, control=control, angle=angle1)
    e1 = ExpectationValue(U=U1, H=H1)
    added = VectorObjective(argsets=[[e1.args[0], angle1]], transformations=[np.true_divide])
    val = simulate(added, variables=variables, backend=simulator)
    en1 = simulate(e1, variables=variables, backend=simulator)
    an1 = -np.sin(angle1(variables=variables))
    anval = angle1(variables=variables)
    dO = grad(added, 'angle1')
    dE = grad(e1, 'angle1')
    deval = simulate(dE, variables=variables, backend=simulator)
    doval = simulate(dO, variables=variables, backend=simulator)
    dtrue = deval / anval - en1 / (anval ** 2)
    assert np.isclose(float(val), float(np.true_divide(en1, anval)))
    assert np.isclose(en1, an1, atol=1.e-4)
    assert np.isclose(doval, dtrue, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_inside(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}
    prod = angle1 * angle2
    qubit = 0
    control = None
    H = paulis.Y(qubit=qubit)
    U = gates.Rx(target=qubit, control=control, angle=prod)
    Up = gates.Rx(target=qubit, control=control, angle=prod + np.pi / 2)
    Down = gates.Rx(target=qubit, control=control, angle=prod - np.pi / 2)
    e1 = ExpectationValue(U=U, H=H)
    en1 = simulate(e1, variables=variables, backend=simulator)
    uen = simulate(0.5 * ExpectationValue(Up, H), variables=variables, backend=simulator)
    den = simulate(-0.5 * ExpectationValue(Down, H), variables=variables, backend=simulator)
    an1 = -np.sin(prod(variables=variables))
    anval = prod(variables=variables)
    an2 = angle2(variables=variables)
    dP = grad(prod, 'angle1')
    dE = grad(e1, 'angle1')
    deval = simulate(dE, variables=variables, backend=simulator)
    dpval = simulate(dP, variables=variables, backend=simulator)
    dtrue = an2 * (uen + den)
    assert np.isclose(en1, an1, atol=1.e-4)
    assert np.isclose(deval, dtrue, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_awkward_expression(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                            value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}

    prod = angle1 * angle2
    qubit = 0
    control = None
    H = paulis.Y(qubit=qubit)
    U = gates.Rx(target=qubit, control=control, angle=prod)
    Up = gates.Rx(target=qubit, control=control, angle=prod + np.pi / 2)
    Down = gates.Rx(target=qubit, control=control, angle=prod - np.pi / 2)
    e1 = ExpectationValue(U=U, H=H)
    en1 = simulate(e1, variables=variables, backend=simulator)
    uen = simulate(0.5 * ExpectationValue(Up, H), variables=variables, backend=simulator)
    den = simulate(-0.5 * ExpectationValue(Down, H), variables=variables, backend=simulator)
    an1 = -np.sin(prod(variables=variables))
    anval = prod(variables=variables)
    an2 = angle2(variables=variables)
    added = angle1 * e1
    dO = grad(added, 'angle1')
    dE = grad(e1, 'angle1')
    deval = simulate(dE, variables=variables, backend=simulator)
    doval = simulate(dO, variables=variables, backend=simulator)
    dtrue = angle1(variables=variables) * deval + en1
    assert np.isclose(en1, an1)
    assert np.isclose(deval, an2 * (uen + den), atol=1.e-4)
    assert np.isclose(doval, dtrue, atol=1.e-4)


@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_really_awful_thing(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                            value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    angle1 = Variable(name="angle1")
    angle2 = Variable(name="angle2")
    variables = {angle1: value1, angle2: value2}

    prod = angle1 * angle2
    qubit = 0
    control = None
    H = paulis.Y(qubit=qubit)
    U = gates.Rx(target=qubit, control=control, angle=prod)
    Up = gates.Rx(target=qubit, control=control, angle=prod + np.pi / 2)
    Down = gates.Rx(target=qubit, control=control, angle=prod - np.pi / 2)
    e1 = ExpectationValue(U=U, H=H)
    en1 = simulate(e1, variables=variables, backend=simulator)
    uen = simulate(0.5 * ExpectationValue(Up, H), variables=variables, backend=simulator)
    den = simulate(-0.5 * ExpectationValue(Down, H), variables=variables, backend=simulator)
    an1 = -np.sin(prod(variables=variables))
    anval = prod(variables=variables)
    an2 = angle2(variables=variables)
    added = angle1 * e1
    raised = added.wrap(np.sin)
    dO = grad(raised, 'angle1')
    dE = grad(e1, 'angle1')
    dA = grad(added, 'angle1')
    val = simulate(added, variables=variables, backend=simulator)
    dave = simulate(dA, variables=variables, backend=simulator)
    deval = simulate(dE, variables=variables, backend=simulator)
    doval = simulate(dO, variables=variables, backend=simulator)
    dtrue = np.cos(val) * dave
    assert np.isclose(en1, an1, atol=1.e-4)
    assert np.isclose(deval, an2 * (uen + den), atol=1.e-4)
    assert np.isclose(doval, dtrue, atol=1.e-4)

def test_stacking():
    a=Variable('a')
    b=Variable('b')
    def f(x):
        return np.cos(x)**2. + np.sin(x)**2.
    funcs=[f,f,f,f]
    vals = {Variable('a'):numpy.random.uniform(0,np.pi),Variable('b'):numpy.random.uniform(0,np.pi)}
    O = VectorObjective(argsets=[[a], [b], [a], [b]], transformations=funcs)
    O1 = O.apply_op_list(funcs)
    O2 = O1/4
    output = simulate(O2,variables=vals)
    assert np.isclose(1.,np.sum(output))

@pytest.mark.parametrize("simulator", [tequila.simulators.simulator_api.pick_backend("random"), tequila.simulators.simulator_api.pick_backend()])
def test_stacking_quantum(simulator, value1=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0)),
                value2=(numpy.random.randint(0, 1000) / 1000.0 * (numpy.pi / 2.0))):
    a = Variable('a')
    b = Variable('b')
    values = {a: value1, b: value2}
    H1 = tq.paulis.X(0)
    H2 = tq.paulis.Y(0)
    U1= tq.gates.Ry(angle=a,target=0)
    U2= tq.gates.Rx(angle=b,target=0)
    e1=ExpectationValue(U1,H1)
    e2=ExpectationValue(U2,H2)
    stacked= tq.objective.stack_objectives([e1,e2])
    out=simulate(stacked,variables=values,backend=simulator)
    v1=out[0]
    v2=out[1]
    an1= np.sin(a(values))
    an2= -np.sin(b(values))
    assert np.isclose(v1+v2,an1+an2)
    # not gonna contract, lets make gradient do some real work
    ga=grad(stacked,a)
    gb=grad(stacked,b)
    tota= np.sum([tq.simulate(x,variables=values) for x in ga])
    totb= np.sum([tq.simulate(x,variables=values) for x in gb])
    gan1= np.cos(a(values))
    gan2= -np.cos(b(values))
    assert np.isclose(tota+totb,gan1+gan2)
