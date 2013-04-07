from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime
from rx.disposables import Disposable, SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class RxException(Exception):
    pass

# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)

class BooleanDisposable(object):
    def __init__(self):
        self.is_disposed = false
    
    def dispose(self):
        self.is_disposed = True
        return self.is_disposed

def test_return_basic():
    scheduler = TestScheduler()

    def factory():
        return Observable.return_value(42, scheduler)
    
    results = scheduler.start(factory)
    results.messages.assert_equal(
                        on_next(201, 42),
                        on_completed(201))


def test_return_disposed():
    scheduler = TestScheduler()

    def factory():
        return Observable.return_value(42, scheduler)
    
    results = scheduler.start(factory, disposed=200)
    results.messages.assert_equal()

def test_return_disposed_after_next():
    scheduler = TestScheduler()
    d = SerialDisposable()
    xs = Observable.return_value(42, scheduler)
    results = scheduler.create_observer()

    def action(scheduler, state):
        def on_next(x):
            d.dispose()
            results.on_next(x)
        def on_error(e):
            results.on_error(e)
        def on_completed():
            results.on_completed()

        d.disposable = xs.subscribe(on_next, on_error, on_completed)
        return d.disposable
    
    scheduler.schedule_absolute(100, action)
    scheduler.start()
    results.messages.assert_equal(on_next(101, 42))

def test_return_observer_throws():
    scheduler1 = TestScheduler()
    xs = Observable.return_value(1, scheduler1)
    xs.subscribe(lambda x: _raise('ex'))
    
    try:
        scheduler1.start()
    except RxException:
        pass
    
    scheduler2 = TestScheduler()
    ys = Observable.return_value(1, scheduler2)
    ys.subscribe(lambda x: x, lambda ex: ex, lambda: _raise('ex'))

    try:
        scheduler2.start()
    except RxException:
        pass

def test_never_basic():
    scheduler = TestScheduler()
    xs = Observable.never()
    results = scheduler.create_observer()
    xs.subscribe(results)
    scheduler.start()
    results.messages.assert_equal()

def test_throw_exception_basic():
    scheduler = TestScheduler()
    ex = 'ex'

    def factory():
        return Observable.throw_exception(ex, scheduler)
    
    results = scheduler.start(factory)
    results.messages.assert_equal(on_error(201, ex))

def test_throw_disposed():
    scheduler = TestScheduler()
    def factory():
        return Observable.throw_exception('ex', scheduler)

    results = scheduler.start(factory, disposed=200)
    results.messages.assert_equal()

def test_throw_observer_throws():
    scheduler = TestScheduler()
    xs = Observable.throw_exception('ex', scheduler)
    xs.subscribe(lambda x: None, lambda ex: _raise('ex'), lambda: None)
    
    try:
        return scheduler.start()
    except RxException:
        pass

def test_empty_basic():
    scheduler = TestScheduler()

    def factory():
        return Observable.empty(scheduler)
    results = scheduler.start(factory)
    
    results.messages.assert_equal(on_completed(201))

def test_empty_disposed():
    scheduler = TestScheduler()

    def factory():
        return Observable.empty(scheduler)
    
    results = scheduler.start(factory, disposed=200)
    results.messages.assert_equal()

def test_empty_observer_throw_exception():
    scheduler = TestScheduler()
    xs = Observable.empty(scheduler)
    xs.subscribe(lambda x: None, lambda ex: None, lambda: _raise('ex'))
    
    try:
        return scheduler.start()
    except RxException:
        pass
    
def test__subscribe_to_enumerable_finite():
    enumerable_finite = [1, 2, 3, 4, 5]
    scheduler = TestScheduler()
    
    def create():
        return Observable.from_array(enumerable_finite, scheduler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(
                        on_next(201, 1),
                        on_next(202, 2),
                        on_next(203, 3),
                        on_next(204, 4),
                        on_next(205, 5),
                        on_completed(206)
                    )

def test_generate_finite():
    scheduler = TestScheduler()

    def create():
        return Observable.generate(0, 
            lambda x: x <= 3,
            lambda x: x + 1,
            lambda x: x,
            scheduler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(
                        on_next(201, 0),
                        on_next(202, 1),
                        on_next(203, 2),
                        on_next(204, 3),
                        on_completed(205)
                    )

def test_generate_throw_condition():
    scheduler = TestScheduler()
    ex = 'ex'

    def create():
        return Observable.generate(0, 
            lambda x: _raise('ex'),
            lambda x: x + 1,
            lambda x: x,
            scheduler)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(201, ex))

def test_generate_throw_result_selector():
    scheduler = TestScheduler()
    ex = 'ex'

    def create():
        return Observable.generate(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: _raise('ex'),
            scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

# def test_Generate_raise Exception(Iter)ate():
#     ex, results, scheduler
#     scheduler = TestScheduler()
#     ex = 'ex'
#     results = scheduler.start_with_create(function () {
#         return Observable.generate(0, function (x) {
#             return true
#         }, function (x) {
#             raise Exception(ex
#  )       }, function (x) {
#             return x
#         }, scheduler)
    
#     results.messages.assert_equal(
#                         on_next(201, 0),
#                         on_error(202, ex)
#                     )


def test_generate_dispose():
    scheduler = TestScheduler()
    ex = 'ex'

    def create():
        return Observable.generate(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            scheduler)

    results = scheduler.start(create, disposed=203)
    results.messages.assert_equal(
                        on_next(201, 0),
                        on_next(202, 1))

# def test_Defer_Complete():
#     invoked, results, scheduler, xs
#     invoked = 0
#     scheduler = TestScheduler()
#     results = scheduler.start_with_create(function () {
#         return Observable.defer(function () {
#             invoked++
#             xs = scheduler.create_cold_observable(
#                                 on_next(100, scheduler.clock),
#                                 on_completed(200)
#                             )
#             return xs
        
    
#     results.messages.assert_equal(
#                         on_next(300, 200),
#                         on_completed(400)
#                     )
#     equal(1, invoked)
#     return xs.subscriptions.assert_equal(subscribe(200, 400))


def test_defer_error():
    scheduler = TestScheduler()
    invoked = 0
    xs = None
    ex = 'ex'
    
    def create():
        def defer():
            nonlocal invoked, xs
            invoked += 1
            xs = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_error(200, ex))
            return xs
        return Observable.defer(defer)
            
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(300, 200), on_error(400, ex))
    assert (1 == invoked)
    return xs.subscriptions.assert_equal(subscribe(200, 400))

def test_defer_dispose():
    scheduler = TestScheduler()
    invoked = 0
    xs = None

    def create():
        def defer():
            nonlocal invoked, xs
            invoked += 1
            xs = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_next(200, invoked), on_next(1100, 1000))
            return xs
        return Observable.defer(defer)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(300, 200), on_next(400, 1))
    assert(1 == invoked)
    return xs.subscriptions.assert_equal(subscribe(200, 1000))


def test_defer_throw():
    scheduler = TestScheduler()
    invoked = 0
    ex = 'ex'

    def create():
        def defer():
            nonlocal invoked
            invoked += 1
            raise Exception(ex)

        return Observable.defer(defer)
    results = scheduler.start(create)       
    
    results.messages.assert_equal(on_error(200, ex))
    assert(1 == invoked)


# def test_Using_Null():
#     createInvoked, disposable, disposeInvoked, results, scheduler, xs, _d
#     scheduler = TestScheduler()
#     disposeInvoked = 0
#     createInvoked = 0
#     results = scheduler.start_with_create(function () {
#         return Observable.using(function () {
#             disposeInvoked++
#             disposable = null
#             return disposable
#         }, function (d) {
#             _d = d
#             createInvoked++
#             xs = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_completed(200))
#             return xs
        
    
#     strictEqual(disposable, _d)
#     results.messages.assert_equal(on_next(300, 200), on_completed(400))
#     equal(1, createInvoked)
#     equal(1, disposeInvoked)
#     xs.subscriptions.assert_equal(subscribe(200, 400))
#     ok(disposable === null)


# def test_Using_Complete():
#     createInvoked, disposable, disposeInvoked, results, scheduler, xs, _d
#     scheduler = TestScheduler()
#     disposeInvoked = 0
#     createInvoked = 0
#     results = scheduler.start_with_create(function () {
#         return Observable.using(function () {
#             disposeInvoked++
#             disposable = MockDisposable(scheduler)
#             return disposable
#         }, function (d) {
#             _d = d
#             createInvoked++
#             xs = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_completed(200))
#             return xs
        
    
#     strictEqual(disposable, _d)
#     results.messages.assert_equal(on_next(300, 200), on_completed(400))
#     equal(1, createInvoked)
#     equal(1, disposeInvoked)
#     xs.subscriptions.assert_equal(subscribe(200, 400))
#     disposable.disposes.assert_equal(200, 400)


# def test_Using_Error():
#     createInvoked, disposable, disposeInvoked, ex, results, scheduler, xs, _d
#     scheduler = TestScheduler()
#     disposeInvoked = 0
#     createInvoked = 0
#     ex = 'ex'
#     results = scheduler.start_with_create(function () {
#         return Observable.using(function () {
#             disposeInvoked++
#             disposable = MockDisposable(scheduler)
#             return disposable
#         }, function (d) {
#             _d = d
#             createInvoked++
#             xs = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_error(200, ex))
#             return xs
        
    
#     strictEqual(disposable, _d)
#     results.messages.assert_equal(on_next(300, 200), on_error(400, ex))
#     equal(1, createInvoked)
#     equal(1, disposeInvoked)
#     xs.subscriptions.assert_equal(subscribe(200, 400))
#     disposable.disposes.assert_equal(200, 400)


# def test_Using_Dispose():
#     createInvoked, disposable, disposeInvoked, results, scheduler, xs, _d
#     scheduler = TestScheduler()
#     disposeInvoked = 0
#     createInvoked = 0
#     results = scheduler.start_with_create(function () {
#         return Observable.using(function () {
#             disposeInvoked++
#             disposable = MockDisposable(scheduler)
#             return disposable
#         }, function (d) {
#             _d = d
#             createInvoked++
#             xs = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_next(1000, scheduler.clock + 1))
#             return xs
        
    
#     strictEqual(disposable, _d)
#     results.messages.assert_equal(on_next(300, 200))
#     equal(1, createInvoked)
#     equal(1, disposeInvoked)
#     xs.subscriptions.assert_equal(subscribe(200, 1000))
#     disposable.disposes.assert_equal(200, 1000)


# def test_Using_ThrowResourceSelector():
#     createInvoked, disposeInvoked, ex, results, scheduler
#     scheduler = TestScheduler()
#     disposeInvoked = 0
#     createInvoked = 0
#     ex = 'ex'
#     results = scheduler.start_with_create(function () {
#         return Observable.using(function () {
#             disposeInvoked++
#             raise Exception(ex
#  )       }, function (d) {
#             createInvoked++
#             return Observable.never()
        
    
#     results.messages.assert_equal(on_error(200, ex))
#     equal(0, createInvoked)
#     return equal(1, disposeInvoked)


# def test_using_throw_resource_usage():
#     createInvoked, disposable, disposeInvoked, ex, results, scheduler
#     scheduler = TestScheduler()
#     disposeInvoked = 0
#     createInvoked = 0
#     ex = 'ex'
#     disposable = void 0
#     results = scheduler.start_with_create(function () {
#         return Observable.using(function () {
#             disposeInvoked++
#             disposable = MockDisposable(scheduler)
#             return disposable
#         }, function (d) {
#             createInvoked++
#             raise Exception(ex
#  )       
    
#     results.messages.assert_equal(on_error(200, ex))
#     equal(1, createInvoked)
#     equal(1, disposeInvoked)
#     return disposable.disposes.assert_equal(200, 200)


def test_create_next():
    scheduler = TestScheduler()
    def create():
        def subscribe(o):
            o.on_next(1)
            o.on_next(2)
            return lambda: None
        return Observable.create(subscribe)

    results = scheduler.start(create)        
    results.messages.assert_equal(on_next(200, 1), on_next(200, 2))

def test_create_completed():
    scheduler = TestScheduler()
    
    def create():
        def subscribe(o):
            o.on_completed()
            o.on_next(100)
            o.on_error('ex')
            o.on_completed()
            return lambda: None
        return Observable.create(subscribe)
      
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(200))

def test_create_error():
    scheduler = TestScheduler()
    ex = 'ex'

    def create():
        def subscribe(o):
            o.on_error(ex)
            o.on_next(100)
            o.on_error('foo')
            o.on_completed()
            return lambda: None
        return Observable.create(subscribe)

    results = scheduler.start(create)      
    results.messages.assert_equal(on_error(200, ex))


def test_create_exception():
    try:
        return Observable.create(lambda o: _raise('ex')).subscribe()
    except RxException:
        pass

# def test_create_dispose():
#     results, scheduler
#     scheduler = TestScheduler()
#     results = scheduler.start_with_create(function () {
#         return Observable.create(function (o) {
#             isStopped
#             isStopped = false
#             o.on_next(1)
#             o.on_next(2)
#             scheduler.scheduleWithRelative(600, function () {
#                 if (!isStopped) {
#                     return o.on_next(3)
#                 }
            
#             scheduler.scheduleWithRelative(700, function () {
#                 if (!isStopped) {
#                     return o.on_next(4)
#                 }
            
#             scheduler.scheduleWithRelative(900, function () {
#                 if (!isStopped) {
#                     return o.on_next(5)
#                 }
            
#             scheduler.scheduleWithRelative(1100, function () {
#                 if (!isStopped) {
#                     return o.on_next(6)
#                 }
            
#             return function () {
#                 return isStopped = true
#             }
        
    
#     results.messages.assert_equal(on_next(200, 1), on_next(200, 2), on_next(800, 3), on_next(900, 4))


def test_create_observer_throws():
    def subscribe(o):
        o.on_next(1)
        return lambda: None
    try:
        return Observable.create(subscribe).subscribe(lambda x: _raise('ex'))
    except RxException:
        pass

    def subscribe2(o):
        o.on_error('exception')
        return lambda: None
    try:
        return Observable.create(subscribe2).subscribe(on_error=lambda ex: _raise('ex'))
    except RxException:
        pass
    
    def subscribe3(o):
        o.on_completed()
        return lambda: None
    try:
        return Observable.create(subscribe3).subscribe(on_complete=lambda: _raise('ex'))
    except RxException:
        pass

def test_create_with_disposable_next():
    scheduler = TestScheduler()
    def create():
        def subscribe(o):
            o.on_next(1)
            o.on_next(2)
            return Disposable.empty()
        return Observable.create_with_disposable(subscribe)
    results = scheduler.start(create)

    results.messages.assert_equal(on_next(200, 1), on_next(200, 2))


def test_create_with_disposable_completed():
    scheduler = TestScheduler()
    def create():
        def subscribe(o):
            o.on_completed()
            o.on_next(100)
            o.on_error('ex')
            o.on_completed()
            return Disposable.empty()
        return Observable.create_with_disposable(subscribe)
        
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(200))

def test_create_with_disposable_error():
    scheduler = TestScheduler()
    ex = 'ex'
    def create():
        def subscribe(o):
            o.on_error(ex)
            o.on_next(100)
            o.on_error('foo')
            o.on_completed()
            return Disposable.empty()

        return Observable.create_with_disposable(subscribe)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(200, ex))

def test_create_with_disposable_exception():
    try:
        return Observable.create_with_disposable(lambda: o, _raise('ex')).subscribe()
    except RxException:
        pass


# def test_CreateWithDisposable_Dispose():
#     results, scheduler
#     scheduler = TestScheduler()
#     results = scheduler.start_with_create(function () {
#         return Observable.createWithDisposable(function (o) {
#             d
#             d = new BooleanDisposable()
#             o.on_next(1)
#             o.on_next(2)
#             scheduler.scheduleWithRelative(600, function () {
#                 if (!d.isDisposed) {
#                     o.on_next(3)
#                 }
            
#             scheduler.scheduleWithRelative(700, function () {
#                 if (!d.isDisposed) {
#                     o.on_next(4)
#                 }
            
#             scheduler.scheduleWithRelative(900, function () {
#                 if (!d.isDisposed) {
#                     o.on_next(5)
#                 }
            
#             scheduler.scheduleWithRelative(1100, function () {
#                 if (!d.isDisposed) {
#                     o.on_next(6)
#                 }
            
#             return d
        
    
#     results.messages.assert_equal(on_next(200, 1), on_next(200, 2), on_next(800, 3), on_next(900, 4))


def test_create_with_disposable_observer_throws():
    def subscribe1(o):
        o.on_next(1)
        return Disposable.empty()

    def on_next(x):
        _raise('ex')

    try:
        return Observable.create_with_disposable(subscribe1).subscribe(on_next)
    except RxException:
        pass
    
    def subscribe2(o):
        o.on_error('exception')
        return Disposable.empty()

    try:
        return Observable.create_with_disposable(subscribe2).subscribe(on_error=lambda ex: _raise('ex'))
    except RxException:
        pass
    
    def subscribe3(o):
        o.on_completed()
        return Disposable.empty()

    try:
        return Observable.create_with_disposable(subscribe3).subscribe(on_completed=_raise('ex'))
    except RxException:
        pass
        
def test_range_zero():
    scheduler = TestScheduler()

    def create():
        return Observable.range(0, 0, scheduler)

    results = scheduler.start(create)    
    results.messages.assert_equal(on_completed(201))

def test_range_one():
    scheduler = TestScheduler()

    def create():
        return Observable.range(0, 1, scheduler)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(201, 0), on_completed(202))

def test_range_five():
    scheduler = TestScheduler()

    def create():
        return Observable.range(10, 5, scheduler)

    results = scheduler.start(create)
    
    results.messages.assert_equal(
                        on_next(201, 10),
                        on_next(202, 11),
                        on_next(203, 12),
                        on_next(204, 13),
                        on_next(205, 14),
                        on_completed(206))

def test_range_dispose():
    scheduler = TestScheduler()

    def create():
        return Observable.range(-10, 5, scheduler)

    results = scheduler.start(create, disposed=204)
    results.messages.assert_equal(on_next(201, -10), on_next(202, -9), on_next(203, -8))

def test_repeat_observable_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(
                        on_next(100, 1),
                        on_next(150, 2),
                        on_next(200, 3),
                        on_completed(250))
    results = scheduler.start(lambda: xs.repeat())
    
    results.messages.assert_equal(
                        on_next(300, 1),
                        on_next(350, 2),
                        on_next(400, 3),
                        on_next(550, 1),
                        on_next(600, 2),
                        on_next(650, 3),
                        on_next(800, 1),
                        on_next(850, 2),
                        on_next(900, 3))
    xs.subscriptions.assert_equal(
                        subscribe(200, 450),
                        subscribe(450, 700),
                        subscribe(700, 950),
                        subscribe(950, 1000))


def test_repeat_observable_infinite():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
    results = scheduler.start(lambda: xs.repeat())
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
    return xs.subscriptions.assert_equal(subscribe(200, 1000))

def test_repeat_observable_error():
    results = None
    scheduler = TestScheduler()
    ex = 'ex'
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_error(250, ex))
    results = scheduler.start(lambda: xs.repeat())
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_error(450, ex))
    return xs.subscriptions.assert_equal(subscribe(200, 450))


# def test_Repeat_Observable_raise Exception(():
# )    d, scheduler1, scheduler2, scheduler3, xs, xss, ys, zs
#     scheduler1 = TestScheduler()
#     xs = Observable.return_value(1, scheduler1).repeat()
#     xs.subscribe(function (x) {
#         raise Exception('ex')
    
#     raises(function () {
#         return scheduler1.start()
    
#     scheduler2 = TestScheduler()
#     ys = Observable.raise Exception(xcep)tion('ex', scheduler2).repeat()
#     ys.subscribe(function (x) { }, function (ex) {
#         raise Exception('ex')
    
#     raises(function () {
#         return scheduler2.start()
    
#     scheduler3 = TestScheduler()
#     zs = Observable.return_value(1, scheduler3).repeat()
#     d = zs.subscribe(function (x) { }, function (ex) { }, function () {
#         raise Exception('ex')
    
#     scheduler3.schedule_absolute(210, function () {
#         return d.dispose()
    
#     scheduler3.start()
#     xss = Observable.create(function (o) {
#         raise Exception('ex')
#     .repeat()
#     raises(function () {
#         return xss.subscribe()
    


def test_repeat_observable_repeat_count_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_completed(20))
    results = scheduler.start(lambda: xs.repeat(3))
    
    results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2), on_next(235, 3), on_next(245, 1), on_next(250, 2), on_next(255, 3), on_completed(260))
    xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 240), subscribe(240, 260))

def test_repeat_observable_repeat_count_dispose():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_completed(20))
    results = scheduler.start(lambda: xs.repeat(3), disposed=231)
    results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2))
    return xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 231))

def test_repeat_observable_repeat_count_infinite():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
    results = scheduler.start(lambda: xs.repeat(3))
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
    return xs.subscriptions.assert_equal(subscribe(200, 1000))

def test_repeat_observable_repeat_count_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_error(250, ex))
    results = scheduler.start(lambda: xs.repeat(3))
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_error(450, ex))
    return xs.subscriptions.assert_equal(subscribe(200, 450))


# def test_Repeat_Observable_RepeatCount_Throws():
#     d, scheduler1, scheduler2, scheduler3, xs, xss, ys, zs
#     scheduler1 = TestScheduler()
#     xs = Observable.return_value(1, scheduler1).repeat(3)
#     xs.subscribe(function (x) {
#         raise Exception('ex')
    
#     raises(function () {
#         return scheduler1.start()
    
#     scheduler2 = TestScheduler()
#     ys = Observable.throwException('ex1', scheduler2).repeat(3)
#     ys.subscribe(function () { }, function (ex) {
#         raise Exception('ex2)'
    
#     raises(function () {
#         return scheduler2.start()
    
#     scheduler3 = TestScheduler()
#     zs = Observable.return_value(1, scheduler3).repeat(100)
#     d = zs.subscribe(function () { }, function (ex) { }, function () {
#         raise Exception('ex3)'
    
#     scheduler3.schedule_absolute(10, function () {
#         return d.dispose()
    
#     scheduler3.start()
#     xss = Observable.create(function (o) {
#         raise Exception('ex4)'
#     .repeat(3)
#     raises(function () {
#         return xss.subscribe()
    
def test_retry_observable_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_completed(250))
    results = scheduler.start(lambda: xs.retry())
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_completed(450))
    xs.subscriptions.assert_equal(subscribe(200, 450))

def test_retry_observable_infinite():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
    results = scheduler.start(lambda: xs.retry())
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
    return xs.subscriptions.assert_equal(subscribe(200, 1000))

def test_retry_observable_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_error(250, ex))
    results = scheduler.start(lambda: xs.retry(), disposed=1100)
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_next(550, 1), on_next(600, 2), on_next(650, 3), on_next(800, 1), on_next(850, 2), on_next(900, 3), on_next(1050, 1))
    return xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950), subscribe(950, 1100))

# def test_Retry_Observable_Throws():
#     d, scheduler1, scheduler2, scheduler3, xs, xss, ys, zs
#     scheduler1 = TestScheduler()
#     xs = Observable.return_value(1, scheduler1).retry()
#     xs.subscribe(function (x) {
#         raise Exception('ex')
    
#     raises(function () {
#         return scheduler1.start()
    
#     scheduler2 = TestScheduler()
#     ys = Observable.throwException('ex', scheduler2).retry()
#     d = ys.subscribe(function (x) { }, function (ex) {
#         raise Exception('ex')
    
#     scheduler2.schedule_absolute(210, function () {
#         return d.dispose()
    
#     scheduler2.start()
#     scheduler3 = TestScheduler()
#     zs = Observable.return_value(1, scheduler3).retry()
#     zs.subscribe(function (x) { }, function (ex) { }, function () {
#         raise Exception('ex')
    
#     raises(function () {
#         return scheduler3.start()
    
#     xss = Observable.create(function (o) {
#         raise Exception('ex')
#     .retry()
#     raises(function () {
#         return xss.subscribe()
    


def test_retry_observable_retry_count_basic():
    scheduler = TestScheduler()
    ex = 'ex'
    xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_error(20, ex))
    results = scheduler.start(lambda: xs.retry(3))
    
    results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2), on_next(235, 3), on_next(245, 1), on_next(250, 2), on_next(255, 3), on_error(260, ex))
    xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 240), subscribe(240, 260))


# def test_Retry_Observable_RetryCount_Dispose():
#     ex, results, scheduler, xs
#     scheduler = TestScheduler()
#     ex = 'ex'
#     xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_error(20, ex))
#     results = scheduler.start_with_dispose(function () {
#         return xs.retry(3)
#     }, 231)
#     results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2))
#     xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 231))


def test_retry_observable_retry_count_dispose():
    scheduler = TestScheduler()
    ex = 'ex'
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
    results = scheduler.start(lambda: xs.retry(3))
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
    xs.subscriptions.assert_equal(subscribe(200, 1000))

def test_retry_observable_retry_count_dispose():
    scheduler = TestScheduler()
    ex = 'ex'
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_completed(250))
    results = scheduler.start(lambda: xs.retry(3))
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_completed(450))
    xs.subscriptions.assert_equal(subscribe(200, 450))


# def test_Retry_Observable_RetryCount_Throws():
#     d, scheduler1, scheduler2, scheduler3, xs, xss, ys, zs
#     scheduler1 = TestScheduler()
#     xs = Observable.return_value(1, scheduler1).retry(3)
#     xs.subscribe(function (x) {
#         raise Exception('ex')
    
#     raises(function () {
#         return scheduler1.start()
    
#     scheduler2 = TestScheduler()
#     ys = Observable.throwException('ex', scheduler2).retry(100)
#     d = ys.subscribe(function (x) { }, function (ex) {
#         raise Exception('ex')
    
#     scheduler2.schedule_absolute(10, function () {
#         return d.dispose()
    
#     scheduler2.start()
#     scheduler3 = TestScheduler()
#     zs = Observable.return_value(1, scheduler3).retry(100)
#     zs.subscribe(function (x) { }, function (ex) { }, function () {
#         raise Exception('ex')
    
#     raises(function () {
#         return scheduler3.start()
    
#     xss = Observable.create(function (o) {
#         raise Exception('ex')
#     .retry(100)
#     raises(function () {
#         return xss.subscribe()
    
def test_repeat_value_count_zero():
    scheduler = TestScheduler()

    def create():
        return Observable.repeat(42, 0, scheduler)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_completed(200))


def test_repeat_value_count_one():
    scheduler = TestScheduler()

    def create():
        return Observable.repeat(42, 1, scheduler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(201, 42), on_completed(201))


def test_repeat_value_count_ten():
    scheduler = TestScheduler()
    
    def create():    
        return Observable.repeat(42, 10, scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(201, 42), on_next(202, 42), on_next(203, 42), on_next(204, 42), on_next(205, 42), on_next(206, 42), on_next(207, 42), on_next(208, 42), on_next(209, 42), on_next(210, 42), on_completed(210))

def test_repeat_value_count_dispose():
    scheduler = TestScheduler()

    def create():
        return Observable.repeat(42, 10, scheduler)

    results = scheduler.start(create, disposed=207)
    results.messages.assert_equal(on_next(201, 42), on_next(202, 42), on_next(203, 42), on_next(204, 42), on_next(205, 42), on_next(206, 42))

def test_repeat_value():
    scheduler = TestScheduler()
    def create():
        return Observable.repeat(42, -1, scheduler)

    results = scheduler.start(create, disposed=207)
    results.messages.assert_equal(on_next(201, 42), on_next(202, 42), on_next(203, 42), on_next(204, 42), on_next(205, 42), on_next(206, 42))

if __name__ == '__main__':
    test_defer_dispose()