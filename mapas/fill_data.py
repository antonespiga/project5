def fill_data(data):
    print(data)
    length = len(data)
    def fill_arr(arr):
        res = []
        last = None
        for i in range(length):
            if i < len(arr) and arr[i] is not None:
                last = arr[i]
                res.append(arr[i])
            else:
                res.append(last)
        return res
    return {
        "coordenadas": data[1],
        

    }