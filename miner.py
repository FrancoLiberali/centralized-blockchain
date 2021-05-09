def main(id, coordinator_queue):
    for i in range(0, 10):
        print(f"{i} - {id}")
        print(coordinator_queue.get())
